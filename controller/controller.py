import threading
import queue

class Controller:
    def __init__(self, controller_queue):
        self.controller_queue = controller_queue

    def generate_commands(self, data):
        # Здесь будет код для генерации команд управления
        print("Контроллер генерирует команды на основе данных:")
        commands = []
        for box in data:
            coords = box.xyxy.cpu().numpy()
            if len(coords) == 4:
                x1, y1, x2, y2 = coords
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                area = (x2 - x1) * (y2 - y1)
                commands.append({"center_x": center_x, "center_y": center_y, "area": area})
        return commands

    def run(self):
        while True:
            data = self.controller_queue.get()
            if data is None:  # Специальный сигнал для завершения работы
                break
            self.generate_commands(data)
            print("Контроллер получил данные и сгенерировал команды")

# Функция для запуска контроллера в отдельном потоке
def start_controller(controller_queue):
    controller = Controller(controller_queue)
    controller.run()
