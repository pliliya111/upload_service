from typing import Annotated

from fastapi import FastAPI, Depends, Body

from dao import get_catalogs, get_table_class_dict, post_table_class_dict, catalog_update_payload_check

from schemas import TableInfo

app = FastAPI()


@app.get("/catalogs/mapping", response_model=list[TableInfo])
async def get_catalog_items():
    data = await get_catalogs()
    return data


@app.get("/catalogs/{catalog_name}")
async def get_catalog_data(catalog_name: str, section_id: int):
    data = await get_table_class_dict(catalog_name, section_id)
    return data


@app.post("/catalogs/{catalog_name}", dependencies=[
    Depends(catalog_update_payload_check)])  # генерация схемы
async def create_catalog_data(catalog: str, body: Annotated[list, Body()]):
    return await post_table_class_dict(catalog, body)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=7000, reload=True)
