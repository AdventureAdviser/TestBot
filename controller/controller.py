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
        self.current_center = None  # Текущие координаты центра объекта

    def generate_commands(self, command):
        if command['command'] == 'center_camera':
            self.simulate_centering_camera(command['center'])
        elif command['command'] == 'move_to_object':
            self.simulate_moving_to_object(command['center'], command['distance'])
        elif command['command'] == 'start_farming':
            self.simulate_farming(command['center'])

    def simulate_centering_camera(self, center):
        print(f"Наведение камеры на центр объекта: {center}")

        # Обновляем текущие координаты центра объекта
        self.current_center = center

        # Координаты центра объекта относительно окна (1280x720)
        screen_width, screen_height = 1280, 720
        window_center_x, window_center_y = screen_width // 2, screen_height // 2

        # Переменная для отслеживания завершения наведения
        completed = False

        while not completed:
            # Расчет смещения от центра экрана до центра объекта
            offset_x = self.current_center[0] - window_center_x
            offset_y = self.current_center[1] - window_center_y

            # Наведение мыши на центр объекта быстрее и плавнее
            steps = 100  # Уменьшаем количество шагов для плавности и быстроты
            for i in range(steps):
                ahk.mouse_move(x=offset_x // steps, y=offset_y // steps, speed=1, relative=True)  # Увеличиваем скорость

                # Очищаем очередь и отправляем сигнал о готовности перед проверкой новых команд
                with self.controller_queue.mutex:
                    self.controller_queue.queue.clear()
                self.response_queue.put({'status': 'ready'})

                # Проверка на наличие новой команды в очереди
                if not self.controller_queue.empty():
                    new_command = self.controller_queue.get()
                    if new_command['command'] == 'center_camera':
                        print(f"Обновлены координаты центра объекта: {new_command['center']}")
                        self.current_center = new_command['center']
                        break  # Прерываем текущий цикл for и перезапускаем перемещение
            else:
                # Если цикл for завершился без прерывания, то наведение завершено
                completed = True

        self.ready = True
        with self.controller_queue.mutex:
            self.controller_queue.queue.clear()
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
                print(f"Отправлена команда на движение к объекту: центр={command['center']}, дистанция={command['distance']}")
            elif command['command'] == 'start_farming':
                print(f"Отправлена команда на фарм объекта: центр={command['center']}")
            self.generate_commands(command)

# Функция для запуска контроллера в отдельном потоке
def start_controller(controller_queue, response_queue):
    controller = Controller(controller_queue, response_queue)
    controller.run()
