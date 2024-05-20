import cv2
import asyncio

async def display_frame(frame_queue):
    """ Отображает обработанные кадры из очереди """
    try:
        while True:
            frame = await frame_queue.get()
            cv2.imshow('Window Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    except asyncio.CancelledError:
        cv2.destroyAllWindows()
        print("Задача отображения отменена")
