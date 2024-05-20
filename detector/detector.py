import cv2
import numpy as np
import pygetwindow as gw
from mss import mss
from ultralytics import YOLO
import asyncio
import concurrent.futures

# Load the YOLOv8 model on the GPU
model = YOLO('best.pt')
model.to('cuda')


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


def process_frame(frame):
    """ Обрабатывает захваченный кадр с использованием модели YOLOv8 для трекинга объектов """
    results = model.track(frame, persist=True, device=0)
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()
        labels = result.boxes.cls.cpu().numpy()

        for box, score, label in zip(boxes, scores, labels):
            x1, y1, x2, y2 = map(int, box)
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            frame = cv2.putText(frame, f'{model.names[int(label)]} {score:.2f}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    return frame


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
            processed_frame = await loop.run_in_executor(pool, process_frame, frame)
            continue_display = await display_frame(processed_frame)
            if not continue_display:
                break


if __name__ == "__main__":
    asyncio.run(main())
