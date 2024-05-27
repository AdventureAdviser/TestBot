from ahk import AHK
import time
import keyboard  # Используем библиотеку keyboard для отслеживания нажатия клавиш

ahk = AHK()

def test_mouse_sensitivity():
    # Устанавливаем начальные координаты в (0, 0)
    # ahk.mouse_move(0, 0, blocking=True)
    # time.sleep(1)  # Ждем стабилизации

    # Запоминаем начальные координаты
    start_pos = ahk.mouse_position
    print(f"Начальная позиция: {start_pos}")

    # Перемещаем мышь медленно на 100 пикселей по оси Y с шагами по 5 пикселей
    steps = 5
    total_move = 0
    for _ in range(20):  # 20 шагов по 5 пикселей = 100 пикселей
        ahk.mouse_move(0, steps, relative=True, blocking=True)
        total_move += steps
        time.sleep(0.1)  # Небольшая пауза между шагами
        current_pos = ahk.mouse_position
        print(f"Текущая позиция: {current_pos}, Общее перемещение: {total_move}")

    time.sleep(1)  # Ждем стабилизации

    # Запоминаем конечные координаты
    end_pos = ahk.mouse_position
    print(f"Конечная позиция: {end_pos}")

    # Вычисляем реальное перемещение по оси Y
    real_move_y = end_pos[1] - start_pos[1]

    # Проверяем, совпадает ли реальное перемещение с ожидаемым
    expected_move = 100
    if real_move_y == expected_move:
        print(f"Перемещение совпадает: {real_move_y} пикселей")
    else:
        print(f"Перемещение не совпадает. Реальное перемещение: {real_move_y} пикселей, Ожидаемое: {expected_move} пикселей")

    # Возвращаем курсор на начальную позицию
    ahk.mouse_move(start_pos[0], start_pos[1], blocking=True)

def on_key(event):
    if event.name == '1':
        test_mouse_sensitivity()

if __name__ == '__main__':
    print("Нажмите клавишу 1 для начала тестирования.")
    keyboard.on_press(on_key)
    keyboard.wait('esc')  # Скрипт будет работать до нажатия клавиши ESC
self.controller_queue.queue.clear()