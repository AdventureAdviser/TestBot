import asyncio
from detector.detector import main as detector_main

if __name__ == "__main__":
    try:
        print("Запуск main.py")
        asyncio.run(detector_main())
        print("main.py завершен")
    except KeyboardInterrupt:
        print("Завершение программы...")
