import cv2
import numpy as np
import pygetwindow as gw
from mss import mss
from ultralytics import YOLO
import asyncio
import time

# Load the YOLOv8 model on the GPU
print("Загрузка модели YOLO...")
model = YOLO('best.pt')
model.to('cuda')
print("Модель YOLO загружена")

# Глобальные параметры для фреймрейта и масштаба
current_fps = 120  # Зададим максимально возможный фреймрейт по умолчанию
current_scale = 1.0  # Изначальный масштаб

async def capture_and_process_window(frame_queue, window_title="ArkAscended"):
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

                results = model(frame, device=0, workers=12)  # Обрабатываем кадр с использованием модели YOLOv8 на GPU
                annotated_frame = results[0].plot()

                await frame_queue.put(annotated_frame)

                # Вычисляем время захвата и обработки кадра, и спим оставшееся время, чтобы поддерживать текущий фреймрейт
                elapsed_time = time.time() - start_time
                time_to_wait = max(0, (1.0 / current_fps) - elapsed_time)
                await asyncio.sleep(time_to_wait)
            except Exception as e:
                print(f"Произошла ошибка в захвате видеопотока: {e}")
                break

async def display_frame(frame_queue):
    """ Отображает обработанные кадры из очереди """
    while True:
        frame = await frame_queue.get()
        cv2.imshow('Window Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

async def main():
    print("Запуск основного процесса...")
    window_title = "ArkAscended"
    frame_queue = asyncio.Queue()

    capture_task = asyncio.create_task(capture_and_process_window(frame_queue, window_title))
    display_task = asyncio.create_task(display_frame(frame_queue))

    await asyncio.gather(capture_task, display_task)

if __name__ == "__main__":
    print("Запуск программы...")
    asyncio.run(main())
    print("Программа завершена")
