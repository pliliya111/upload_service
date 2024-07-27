import os
import threading

import requests

UPLOAD_URL = "http://localhost:5000/upload"  # сервер для загрузки
IMAGES_FOLDER = "images"  # папка откуда загружаем
N = 3  # Максимальное количество параллельных загрузок


def upload_image(file_path, semaphore):
    """
    Загружает изображение на сервер в отдельном потоке.

    Параметры:
    - file_path (str): Путь к файлу изображения, который нужно загрузить.
    - semaphore (threading.Semaphore): Семафор для ограничения количества одновременных загрузок.

    Исключения:
    - Печатает сообщение об ошибке, если возникает исключение при загрузке изображения.
    """
    with semaphore:
        try:
            filename = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                files = {"file": (filename, f)}
                response = requests.post(UPLOAD_URL, files=files)
                if response.status_code == 200:
                    result = response.json()
                    print(f'Успех: {result["message"]}')
                else:
                    print(f"Ошибка загрузки {filename}")
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")


def main():
    """
    Основная функция, которая создаёт и запускает потоки для загрузки изображений из папки IMAGES_FOLDER
    с ограничением на количество параллельных загрузок.
    """
    semaphore = threading.Semaphore(N)
    image_files = [
        os.path.join(IMAGES_FOLDER, img) for img in os.listdir(IMAGES_FOLDER)
    ]

    threads = []
    for img in image_files:
        thread = threading.Thread(target=upload_image, args=(img, semaphore))
        thread.start()
        threads.append(thread)

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
