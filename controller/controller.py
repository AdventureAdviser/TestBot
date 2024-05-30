import threading
import queue
import time
from tqdm import tqdm
from ahk import AHK

ahk = AHK()

class Controller:
    def __init__(self, controller_queue, response_queue, configurator):
        self.controller_queue = controller_queue
        self.response_queue = response_queue
        self.configurator = configurator
        self.ready = True
        self.current_center = (0, 0)

    def generate_commands(self, command):
        if command['command'] == 'center_camera':
            self.simulate_centering_camera(command['center'])
        elif command['command'] == 'move_to_object':
            self.simulate_moving_to_object(command['center'], command['distance'])
        elif command['command'] == 'farm_object':
            self.simulate_farming(command['center'])

    def simulate_centering_camera(self, center):
        print(f"Наведение камеры на центр объекта: {center}")

        # Проверка, зажата ли кнопка "w"
        if not ahk.key_state('w', mode='P'):
            ahk.key_down('w')
            print("Кнопка 'w' зажата")

        if not ahk.key_state('shift', mode='P'):
            ahk.key_down('shift')
            print("Кнопка 'shift' зажата")

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
            offset_y = self.current_center[1] - window_center_y - self.configurator.get_move_distance_threshold()

            # Наведение мыши на центр объекта быстрее и плавнее
            steps = 60  # Уменьшаем количество шагов для плавности и быстроты
            for i in range(steps):
                ahk.mouse_move(x=offset_x // steps, y=offset_y // steps, speed=1, relative=True)

                # Управление поворотами камеры налево и направо
                if offset_x > 0:
                    if not ahk.key_state('d', mode='P'):
                        ahk.key_down('d')
                        print("Кнопка 'd' зажата")
                    if ahk.key_state('a', mode='P'):
                        ahk.key_up('a')
                        print("Кнопка 'a' отпущена")
                elif offset_x < 0:
                    if not ahk.key_state('a', mode='P'):
                        ahk.key_down('a')
                        print("Кнопка 'a' зажата")
                    if ahk.key_state('d', mode='P'):
                        ahk.key_up('d')
                        print("Кнопка 'd' отпущена")
                else:
                    if ahk.key_state('d', mode='P'):
                        ahk.key_up('d')
                        print("Кнопка 'd' отпущена")
                    if ahk.key_state('a', mode='P'):
                        ahk.key_up('a')
                        print("Кнопка 'a' отпущена")

                if offset_y < 0:
                    if not ahk.key_state('x', mode='P'):
                        ahk.key_down('x')
                        print("Кнопка 'x' зажата")
                    if ahk.key_state('c', mode='P'):
                        ahk.key_up('c')
                        print("Кнопка 'c' отпущена")
                elif offset_y > 0:
                    if not ahk.key_state('c', mode='P'):
                        ahk.key_down('c')
                        print("Кнопка 'c' зажата")
                    if ahk.key_state('x', mode='P'):
                        ahk.key_up('x')
                        print("Кнопка 'x' отпущена")
                else:
                    if ahk.key_state('x', mode='P'):
                        ahk.key_up('x')
                        print("Кнопка 'x' отпущена")
                    if ahk.key_state('c', mode='P'):
                        ahk.key_up('c')
                        print("Кнопка 'c' отпущена")

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
                    elif new_command['command'] != 'center_camera':
                        completed = True
                        break  # Прерываем текущий цикл for и перезапускаем перемещение
            else:
                # Если цикл for завершился без прерывания, то наведение завершено
                completed = True

        # Отпускаем кнопки "shift", "x" и "c"
        ahk.key_up('shift')
        print("Кнопка 'shift' отпущена")
        # Отпускаем кнопки "a" и "d" по завершению функции
        if ahk.key_state('d', mode='P'):
            ahk.key_up('d')
            print("Кнопка 'd' отпущена")
        if ahk.key_state('a', mode='P'):
            ahk.key_up('a')
            print("Кнопка 'a' отпущена")

        if ahk.key_state('x', mode='P'):
            ahk.key_up('x')
            print("Кнопка 'x' отпущена")

        if ahk.key_state('c', mode='P'):
            ahk.key_up('c')
            print("Кнопка 'c' отпущена")

        self.ready = True
        with self.controller_queue.mutex:
            self.controller_queue.queue.clear()
        self.response_queue.put({'status': 'ready'})
        print("Контроллер готов к приему новых команд")

    def simulate_moving_to_object(self, center, distance):
        print(f"Движение к объекту: {center}, дистанция: {distance}")

        # Проверка, зажаты ли клавиши "w" и "shift"
        if ahk.key_state('w', mode='P'):
            ahk.key_down('w')
            print("Кнопка 'w' зажата")

        # if not ahk.key_state('shift', mode='P'):
        #     ahk.key_down('shift')
        #     print("Кнопка 'shift' зажата")

        self.current_center = center

        screen_width, screen_height = 1280, 720
        window_center_x, window_center_y = screen_width // 2, screen_height // 2

        completed = False

        while not completed:
            offset_y = self.current_center[1] - window_center_y - self.configurator.get_move_distance_threshold()

            steps = 60
            for i in range(steps):
                ahk.mouse_move(x=0, y=offset_y // steps, speed=1, relative=True)

                # Проверка высоты камеры
                if offset_y < 0:
                    if not ahk.key_state('x', mode='P'):
                        ahk.key_down('x')
                        print("Кнопка 'x' зажата")
                    if ahk.key_state('c', mode='P'):
                        ahk.key_up('c')
                        print("Кнопка 'c' отпущена")
                elif offset_y > 0:
                    if not ahk.key_state('c', mode='P'):
                        ahk.key_down('c')
                        print("Кнопка 'c' зажата")
                    if ahk.key_state('x', mode='P'):
                        ahk.key_up('x')
                        print("Кнопка 'x' отпущена")
                else:
                    if ahk.key_state('x', mode='P'):
                        ahk.key_up('x')
                        print("Кнопка 'x' отпущена")
                    if ahk.key_state('c', mode='P'):
                        ahk.key_up('c')
                        print("Кнопка 'c' отпущена")

                with self.controller_queue.mutex:
                    self.controller_queue.queue.clear()
                self.response_queue.put({'status': 'ready'})

                if not self.controller_queue.empty():
                    new_command = self.controller_queue.get()
                    if new_command['command'] == 'move_to_object':
                        print(f"Обновлены координаты центра объекта: {new_command['center']}")
                        self.current_center = new_command['center']
                        break
                    elif new_command['command'] != 'move_to_object':
                        completed = True
                        break
            else:
                completed = True

        # # Отпускаем кнопки "shift", "x" и "c"
        # ahk.key_up('shift')
        # print("Кнопка 'shift' отпущена")

        if ahk.key_state('x', mode='P'):
            ahk.key_up('x')
            print("Кнопка 'x' отпущена")

        if ahk.key_state('c', mode='P'):
            ahk.key_up('c')
            print("Кнопка 'c' отпущена")

        self.ready = True
        self.response_queue.put({'status': 'ready'})
        print("Контроллер готов к приему новых команд")

    def simulate_farming(self, center):
        print(f"Фарм объекта: {center}")

        # Проверка, зажата ли кнопка "w"
        if ahk.key_state('w', mode='P'):
            ahk.key_up('w')
            print("Кнопка 'w' отпущена")

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
            elif command['command'] == 'farm_object':
                print(f"Отправлена команда на фарм объекта: центр={command['center']}")
            self.generate_commands(command)

# Функция для запуска контроллера в отдельном потоке
def start_controller(controller_queue, response_queue, configurator):
    controller = Controller(controller_queue, response_queue, configurator)
    controller.run()
