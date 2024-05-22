import threading
import queue
import time
from tqdm import tqdm

class Controller:
    def __init__(self, controller_queue, response_queue):
        self.controller_queue = controller_queue
        self.response_queue = response_queue
        self.ready = True

    def generate_commands(self, command):
        if command['command'] == 'center_camera':
            print(f"Наведение камеры на центр объекта: {command['center']}")
            self.simulate_centering_camera(command['center'])
        elif command['command'] == 'move_to_object':
            print(f"Движение к объекту: {command['center']}, дистанция: {command['distance']}")
            self.simulate_moving_to_object(command['center'], command['distance'])

    def simulate_centering_camera(self, center):
        print("Ожидание завершения наведения:")
        for i in tqdm(range(30, 0, -1), desc="Наведение камеры", unit="сек"):
            time.sleep(1)
        self.ready = True
        self.response_queue.put({'status': 'ready'})
        print("Контроллер готов к приему новых команд")

    def simulate_moving_to_object(self, center, distance):
        print("Ожидание завершения движения:")
        for i in tqdm(range(30, 0, -1), desc="Движение к объекту", unit="сек"):
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
            self.generate_commands(command)

# Функция для запуска контроллера в отдельном потоке
def start_controller(controller_queue, response_queue):
    controller = Controller(controller_queue, response_queue)
    controller.run()
