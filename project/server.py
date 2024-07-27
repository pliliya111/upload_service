import os
import aiofiles
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Обрабатывает загрузку файла.

    Параметры:
    - file: Загружаемый файл.

    Возвращает:
    - JSONResponse: Ответ с сообщением о результате загрузки.
    """
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file.file.read())
    return JSONResponse(
        content={"message": f"Файл {file.filename} успешно загружен"},
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
