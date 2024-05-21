import threading
import queue

class Configurator:
    def __init__(self):
        self.current_fps = 60  # Изначальный фреймрейт
        self.current_scale = 0.6  # Изначальный масштаб
        self.current_area_threshold = 2800  # Изначальный порог площади
        self.current_distance_threshold = 100  # Изначальный порог расстояния
        self.config_queue = queue.Queue()

    def set_fps(self, fps):
        self.current_fps = fps
        self.config_queue.put(('fps', fps))
        print(f"FPS updated to: {fps}")

    def set_scale(self, scale):
        self.current_scale = scale
        self.config_queue.put(('scale', scale))
        print(f"Scale updated to: {scale}")

    def set_area_threshold(self, area):
        self.current_area_threshold = area
        self.config_queue.put(('area_threshold', area))
        print(f"Area threshold updated to: {area}")

    def set_distance_threshold(self, distance):
        self.current_distance_threshold = distance
        self.config_queue.put(('distance_threshold', distance))
        print(f"Distance threshold updated to: {distance}")

    def get_fps(self):
        return self.current_fps

    def get_scale(self):
        return self.current_scale

    def get_area_threshold(self):
        return self.current_area_threshold

    def get_distance_threshold(self):
        return self.current_distance_threshold

    def get_config_updates(self):
        updates = []
        while not self.config_queue.empty():
            updates.append(self.config_queue.get())
        return updates

# Функция для запуска конфигуратора в отдельном потоке
def start_configurator(configurator_queue):
    configurator = Configurator()
    while True:
        command, value = configurator_queue.get()
        if command == 'set_fps':
            configurator.set_fps(value)
        elif command == 'set_scale':
            configurator.set_scale(value)
        elif command == 'set_area_threshold':
            configurator.set_area_threshold(value)
        elif command == 'set_distance_threshold':
            configurator.set_distance_threshold(value)
        elif command is None:  # Специальный сигнал для завершения работы
            break
        print(f"Configurator received command: {command} with value: {value}")

# Пример использования
if __name__ == "__main__":
    configurator_queue = queue.Queue()
    configurator_thread = threading.Thread(target=start_configurator, args=(configurator_queue,))
    configurator_thread.start()

    # Пример отправки команд
    configurator_queue.put(('set_fps', 60))
    configurator_queue.put(('set_scale', 1.5))
    configurator_queue.put(('set_area_threshold', 3000))
    configurator_queue.put(('set_distance_threshold', 120))

    # Завершение работы конфигуратора
    configurator_queue.put((None, None))
    configurator_thread.join()
