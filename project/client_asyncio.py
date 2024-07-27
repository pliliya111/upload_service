import asyncio
import os

import aiofiles
import aiohttp

UPLOAD_URL = "http://localhost:5000/upload"
IMAGES_FOLDER = "images"
N = 3  # Максимальное количество параллельных загрузок


# async def upload_image(sem, session, file_path):
#     async with sem:
#         filename = os.path.basename(file_path)
#         print(f'Загрузка {filename}')
#         async with aiofiles.open(file_path, 'rb') as f:
#             files = {'file': (filename, f)}
#             async with session.post(UPLOAD_URL, **files) as response:
#                 print(response.url_obj)
#                 if response.status == 200:
#                     result = await response.json()
#                     print(f'Success: {result["message"]}')
#                 else:
#                     print(f'Failed to upload {filename}')


async def upload_file(file_path, url):
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field(
                "file",
                f,
                filename=file_path.split("/")[-1],
                content_type="application/octet-stream",
            )
            async with session.post(url, data=data) as response:
                print(await response.json())


async def main():
    sem = asyncio.Semaphore(N)
    tasks = []
    for image in os.listdir(IMAGES_FOLDER):
        file_path = os.path.join(IMAGES_FOLDER, image)
        tasks.append(upload_file(sem, file_path))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
