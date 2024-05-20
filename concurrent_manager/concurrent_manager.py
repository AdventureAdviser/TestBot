import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed


class ConcurrentManager:
    def __init__(self, max_workers=4):
        """
        Инициализация менеджера асинхронности и многопоточности с заданным максимальным числом одновременных потоков.
        """
        self.tasks_queue = queue.Queue()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def add_task(self, func, *args, **kwargs):
        """
        Добавление задачи в очередь задач. Принимает функцию и её аргументы.
        """
        self.tasks_queue.put((func, args, kwargs))

    def process_tasks(self):
        """
        Обработка задач из очереди в многопоточном режиме.
        """
        futures = []
        while not self.tasks_queue.empty():
            func, args, kwargs = self.tasks_queue.get()
            future = self.executor.submit(func, *args, **kwargs)
            futures.append(future)

        for future in as_completed(futures):
            try:
                result = future.result()
                print(f"Задача выполнена с результатом: {result}")
            except Exception as e:
                print(f"Произошла ошибка при выполнении задачи: {str(e)}")

    def shutdown(self):
        """
        Завершение работы исполнителя и освобождение ресурсов.
        """
        self.executor.shutdown(wait=True)
        print("Менеджер асинхронности успешно завершил работу.")


# Пример использования
if __name__ == "__main__":
    def task_to_run(param):
        return f"задача выполнена с параметром {param}"


    manager = ConcurrentManager(max_workers=4)
    for i in range(10):
        manager.add_task(task_to_run, param=i)

    manager.process_tasks()
    manager.shutdown()
