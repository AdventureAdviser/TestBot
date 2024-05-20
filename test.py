import cv2
import numpy as np
import pygetwindow as gw
from mss import mss

def list_windows():
    """ Печатает список всех открытых окон """
    windows = gw.getAllTitles()
    return [window for window in windows if window]

def select_window(window_title):
    """ Захватывает и отображает поток из выбранного окна в реальном времени """
    sct = mss()
    while True:
        try:
            # Получение информации о размерах и позиции окна
            window = gw.getWindowsWithTitle(window_title)[0]
            if window:
                window.restore()
                monitor = {"top": window.top, "left": window.left, "width": window.width, "height": window.height}

                # Скриншот выбранной области
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Обратите внимание на использование BGRA

                # Показать кадр
                cv2.imshow('Window Stream', frame)

                # Завершение цикла по нажатию 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            break

    cv2.destroyAllWindows()

# Получение списка окон
windows = list_windows()
print("Доступные окна:")
for i, window in enumerate(windows):
    print(f"{i + 1}: {window}")

# Пользователь вводит номер нужного окна
selected_index = int(input("Введите номер окна для захвата: ")) - 1
selected_window = windows[selected_index]

# Запуск захвата изображения из окна
select_window(selected_window)
