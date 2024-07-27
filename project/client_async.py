import asyncio
import os

import aiohttp

UPLOAD_URL = "http://localhost:5000/upload"  # сервер для загрузки
IMAGES_FOLDER = "images"  # папка откуда загружаем
N = 3  # Максимальное количество параллельных загрузок


async def upload_file(sem, file_path):
    """
    Асинхронно загружает файл на сервер.

    Параметры:
    - sem (asyncio.Semaphore): Семафор для ограничения количества одновременных загрузок.
    - file_path (str): Путь к файлу, который нужно загрузить.

    Исключения:
    - Печатает сообщение об ошибке, если что-то пошло не так при загрузке файла.
    """
    async with sem:
        try:
            filename = os.path.basename(file_path)
            async with aiohttp.ClientSession() as session:
                with open(file_path, "rb") as f:
                    data = aiohttp.FormData()
                    data.add_field(
                        "file",
                        f,
                        filename=filename,
                        content_type="application/octet-stream",
                    )
                    async with session.post(UPLOAD_URL, data=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            print(f'Успех: {result["message"]}')
                        else:
                            print(f"Ошибка загрузки {filename}")
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")


async def main():
    """
    Основная функция, которая собирает и запускает задачи для загрузки всех файлов
    из папки IMAGES_FOLDER с ограничением на количество одновременных загрузок.
    """
    sem = asyncio.Semaphore(N)
    tasks = []
    for image in os.listdir(IMAGES_FOLDER):
        file_path = os.path.join(IMAGES_FOLDER, image)
        if os.path.isfile(file_path):
            tasks.append(upload_file(sem, file_path))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
