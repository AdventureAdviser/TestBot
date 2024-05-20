import cv2
import asyncio
import threading
import queue

class Streamer:
    def __init__(self, frame_queue):
        self.frame_queue = frame_queue

    def display_frame(self):
        """ Отображает обработанные кадры из очереди """
        try:
            while True:
                frame = self.frame_queue.get()
                if frame is None:
                    break
                cv2.imshow('Window Stream', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
        except Exception as e:
            cv2.destroyAllWindows()
            print(f"Произошла ошибка в отображении видеопотока: {e}")

def start_streamer(frame_queue):
    streamer = Streamer(frame_queue)
    streamer.display_frame()
