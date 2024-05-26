import threading
import queue
import time
from tqdm import tqdm
from ahk import AHK


class Controller:
    def __init__(self, controller_queue, response_queue):
        self.controller_queue = controller_queue
        self.response_queue = response_queue
        self.ready = True
        self.ahk = AHK()

    def generate_commands(self, command):
        if command['command'] == 'center_camera':
            self.simulate_centering_camera(command['center'])
        elif command['command'] == 'move_to_object':
            self.simulate_moving_to_object(command['center'], command['distance'])
        elif command['command'] == 'start_farming':
            self.simulate_farming(command['center'])

    def simulate_centering_camera(self, center):
        print(f"Наведение камеры на центр объекта: {center}")

        # Получаем текущую позицию мыши
        current_pos = self.ahk.mouse_position

        # Вычисляем вектор смещения
        dx = center[0] - current_pos[0]
        dy = center[1] - current_pos[1]

        # Плавное перемещение мыши
        steps = 100  # Увеличено количество шагов для более плавного перемещения
        for step in range(steps):
            new_x = current_pos[0] + (dx * (step + 1) / steps)
            new_y = current_pos[1] + (dy * (step + 1) / steps)
            self.ahk.mouse_move(x=new_x, y=new_y, blocking=True)
            time.sleep(0.01)  # Уменьшена задержка для более плавного перемещения

        # Завершение наведения
        self.ready = True
        self.response_queue.put({'status': 'ready'})
        print("Контроллер готов к приему новых команд")

    def simulate_moving_to_object(self, center, distance):
        print(f"Движение к объекту: {center}, дистанция: {distance}")
        for i in tqdm(range(30, 0, -1), desc="Движение к объекту", unit="сек"):
            time.sleep(1)
        self.ready = True
        self.response_queue.put({'status': 'ready'})
        print("Контроллер готов к приему новых команд")

    def simulate_farming(self, center):
        print(f"Фарм объекта: {center}")
        for i in tqdm(range(30, 0, -1), desc="Фарм объекта", unit="сек"):
            time.sleep(1)
        self.ready = True
        self.response_queue.put({'status': 'ready'})
        print("Контроллер готов к приему новых команд")

    def run(self):
        while True:
            command = self.controller_queue.get()
            if command is None:  # Специальный сигнал для завершения работы
                break
            self.ready = False
            if command['command'] == 'center_camera':
                print(f"Отправлена команда на наведение камеры на центр объекта: центр={command['center']}")
            elif command['command'] == 'move_to_object':
                print(
                    f"Отправлена команда на движение к объекту: центр={command['center']}, дистанция={command['distance']}")
            elif command['command'] == 'start_farming':
                print(f"Отправлена команда на фарм объекта: центр={command['center']}")
            self.generate_commands(command)


# Функция для запуска контроллера в отдельном потоке
def start_controller(controller_queue, response_queue):
    controller = Controller(controller_queue, response_queue)
    controller.run()
