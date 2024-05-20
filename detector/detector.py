import cv2
import numpy as np
import pygetwindow as gw
from mss import mss
from ultralytics import YOLO
import asyncio
import time
import logging
import queue
import threading
from collections import defaultdict
from controller.controller import start_controller
from streamer.streamer import start_streamer

# Отключаем логирование ultralytics
logging.getLogger('ultralytics').setLevel(logging.WARNING)

# Load the YOLOv8 model on the GPU
print("Загрузка модели YOLO...")
model = YOLO('best.pt')
model.to('cuda')
print("Модель YOLO загружена")

# Глобальные параметры для фреймрейта и масштаба
current_fps = 120  # Зададим максимально возможный фреймрейт по умолчанию
current_scale = 1.0  # Изначальный масштаб
track_history = defaultdict(lambda: [])


async def capture_and_process_window(frame_queue, controller_queue, window_title="ArkAscended"):
    """ Захватывает видеопоток из указанного окна, обрабатывает и отправляет в очередь """
    print("Запуск захвата видеопотока...")
    sct = mss()
    window = gw.getWindowsWithTitle(window_title)[0]
    if window:
        window.restore()
        monitor = {"top": window.top, "left": window.left, "width": window.width, "height": window.height}
        while True:
            try:
                start_time = time.time()
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                # Масштабируем изображение
                if current_scale != 1.0:
                    width = int(frame.shape[1] * current_scale)
                    height = int(frame.shape[0] * current_scale)
                    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)

                # Обрабатываем кадр с использованием модели YOLOv8 на GPU и трекера ByteTrack
                results = model.track(frame, device=0, workers=12, tracker='bytetrack.yaml', persist=True, verbose=False)
                annotated_frame = results[0].plot()

                # Визуализация треков
                if results[0].boxes.id is not None:
                    track_ids = results[0].boxes.id.int().cpu().tolist()
                    centers = [(int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)) for box in
                               results[0].boxes.xyxy]

                    for track_id, center in zip(track_ids, centers):
                        track_history[track_id].append(center)
                        for i in range(1, len(track_history[track_id])):
                            cv2.line(annotated_frame, track_history[track_id][i - 1], track_history[track_id][i],
                                     color=(0, 255, 0), thickness=2)

                await frame_queue.put(annotated_frame)

                # Отправляем результаты в очередь контроллера
                controller_queue.put(results[0].boxes)

                # Вычисляем время захвата и обработки кадра, и спим оставшееся время, чтобы поддерживать текущий фреймрейт
                elapsed_time = time.time() - start_time
                time_to_wait = max(0, (1.0 / current_fps) - elapsed_time)
                await asyncio.sleep(time_to_wait)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Произошла ошибка в захвате видеопотока: {e}")
                break


async def main():
    print("Запуск основного процесса...")
    window_title = "ArkAscended"
    frame_queue = asyncio.Queue()
    controller_queue = queue.Queue()  # Используем потокобезопасную очередь для контроллера
    frame_queue_for_streamer = queue.Queue()

    # Запуск контроллера в отдельном потоке
    controller_thread = threading.Thread(target=start_controller, args=(controller_queue,))
    controller_thread.start()

    # Запуск стримера в отдельном потоке
    streamer_thread = threading.Thread(target=start_streamer, args=(frame_queue_for_streamer,))
    streamer_thread.start()

    async def relay_frames():
        while True:
            frame = await frame_queue.get()
            frame_queue_for_streamer.put(frame)
            if frame is None:
                break

    capture_task = asyncio.create_task(capture_and_process_window(frame_queue, controller_queue, window_title))
    relay_task = asyncio.create_task(relay_frames())

    try:
        await asyncio.gather(capture_task, relay_task)
    except asyncio.CancelledError:
        capture_task.cancel()
        relay_task.cancel()
        await capture_task
        await relay_task

    # Завершение работы контроллера
    controller_queue.put(None)
    controller_thread.join()

    # Завершение работы стримера
    frame_queue_for_streamer.put(None)
    streamer_thread.join()


if __name__ == "__main__":
    try:
        print("Запуск программы...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Завершение программы...")
