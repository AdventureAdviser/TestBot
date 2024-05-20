import cv2
import numpy as np
import pygetwindow as gw
from mss import mss
from ultralytics import YOLO
import asyncio
import concurrent.futures
import time

# Load the YOLOv8 model on the GPU
model = YOLO('best.pt')
model.to('cuda')

# Глобальные параметры для фреймрейта и масштаба
current_fps = 30  # Изначальный фреймрейт
current_scale = 1.0  # Изначальный масштаб


async def capture_window(window_title="ArkAscended"):
    """ Захватывает видеопоток из указанного окна в реальном времени """
    sct = mss()
    window = gw.getWindowsWithTitle(window_title)[0]
    if window:
        window.restore()
        monitor = {"top": window.top, "left": window.left, "width": window.width, "height": window.height}
        while True:
            try:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                yield frame
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                break


def process_frame(frame, scale, fps):
    """ Обрабатывает захваченный кадр с использованием модели YOLOv8 для трекинга объектов """
    start_time = time.time()

    # Масштабируем изображение
    if scale != 1.0:
        width = int(frame.shape[1] * scale)
        height = int(frame.shape[0] * scale)
        frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)

    results = model(frame)

    # Используем встроенную функцию для отрисовки результатов
    annotated_frame = results[0].plot()

    # Контролируем фреймрейт
    elapsed_time = time.time() - start_time
    time_to_wait = max(0, (1.0 / fps) - elapsed_time)
    time.sleep(time_to_wait)

    return annotated_frame


async def display_frame(frame):
    """ Отображает обработанный кадр в окне """
    cv2.imshow('Window Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        return False
    return True


async def main():
    window_title = "ArkAscended"
    loop = asyncio.get_running_loop()
    async for frame in capture_window(window_title):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            processed_frame = await loop.run_in_executor(pool, process_frame, frame, current_scale, current_fps)
            continue_display = await display_frame(processed_frame)
            if not continue_display:
                break


if __name__ == "__main__":
    asyncio.run(main())
