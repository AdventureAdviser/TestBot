import threading
import queue
import time
from tqdm import tqdm
from ahk import AHK

ahk = AHK()

class Controller:
    def __init__(self, controller_queue, response_queue):
        self.controller_queue = controller_queue
        self.response_queue = response_queue
        self.ready = True

    def generate_commands(self, command):
        if command['command'] == 'center_camera':
            self.simulate_centering_camera(command['center'])
        elif command['command'] == 'move_to_object':
            self.simulate_moving_to_object(command['center'], command['distance'])
        elif command['command'] == 'start_farming':
            self.simulate_farming(command['center'])

    def simulate_centering_camera(self, center):
        print(f"Наведение камеры на центр объекта: {center}")

        object_center_x, object_center_y = center
        screen_width, screen_height = 1280, 720
        window_center_x, window_center_y = screen_width // 2, screen_height // 2

        # Смещения от центра экрана до центра объекта
        offset_x = object_center_x - window_center_x
        offset_y = object_center_y - window_center_y

        # Двигаем мышь в сторону центра объекта
        ahk.mouse_move(x=offset_x // 10, y=offset_y // 10, speed=300, relative=True)
        # time.sleep(0.5)  # Небольшая задержка

        # for i in tqdm(range(5, 0, -1), desc="Тестовый отсчет", unit="сек"):
        #     time.sleep(1)

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
            if command is None:
                break
            self.ready = False
            if command['command'] == 'center_camera':
                print(f"Отправлена команда на наведение камеры на центр объекта: центр={command['center']}")
            elif command['command'] == 'move_to_object':
                print(f"Отправлена команда на движение к объекту: центр={command['center']}, дистанция={command['distance']}")
            elif command['command'] == 'start_farming':
                print(f"Отправлена команда на фарм объекта: центр={command['center']}")
            self.generate_commands(command)

def start_controller(controller_queue, response_queue):
    controller = Controller(controller_queue, response_queue)
    controller.run()
