from fastapi import Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, select, insert, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from models import Base, IndicatorValueVariety, Indicators, Section

engine = create_engine('sqlite:///example.db', connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Глобальный объект, который сопоставляет названия таблиц и модели
# Желательно заполнить при старте приложения (перенести в startup, например)
table_class_dict = {}


def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()


def get_class_by_tablename(tablename):
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c


async def get_catalogs():
    tables = Base.metadata.tables
    res = []
    for table in tables.values():
        columns_info = []
        table_info = getattr(table, 'info', {})
        if table_info.get('type') == 'reference':
            for col in table.columns:
                foreign_key = None
                if col.foreign_keys:
                    fk = next(iter(col.foreign_keys))
                    foreign_key = {
                        "column": fk.column.name,
                        "table": fk.column.table.name
                    }
                columns_info.append({
                    "name": col.name,
                    "title": col.comment,
                    "type": str(col.type),
                    "rewuired": not col.nullable,
                    "foreign_key": foreign_key
                })
            res.append({"name": table.name, "title": table.comment, "columns": columns_info})
    return res


async def get_schema(catalog_name: str):
    init_table_class_dict()
    table_model = table_class_dict.get(catalog_name)
    if not table_model:
        return None
    return get_schema(table_model)


def init_table_class_dict():
    """Заполнение table_class_dict - Глобальный объект, который сопоставляет названия таблиц и модели"""
    if not table_class_dict:
        for cls in Base.registry.mappers:
            if hasattr(cls.class_, '__tablename__'):
                table_class_dict[cls.class_.__tablename__] = cls.class_


async def get_table_class_dict(catalog_name, section_id):
    init_table_class_dict()
    session = next(get_db())
    try:
        table_model = table_class_dict[catalog_name]
        query = select(table_model)
        result = session.execute(query).scalars().fetchall()
        print(type(result[0]), dir(result[0]))
        data = [row.as_dict() for row in result if row.section_id == section_id]
        return data
    except SQLAlchemyError as e:
        session.rollback()
        return {"result": "error", "message": str(e)}


async def catalog_update_payload_check(*, request: Request, catalog: str) -> bool:
    """Валидирует данные запроса для изменения элемента справочника."""
    init_table_class_dict()
    data = await request.json()
    table_model = table_class_dict.get(catalog)
    if not table_model:
        raise HTTPException(status_code=404, detail=f"Table {catalog} not found")
    model = table_model.get_schema()
    try:
        if isinstance(data, list):
            for i in data:
                model(**i)
        else:
            model(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return True


async def post_table_class_dict(catalog_name, data):
    init_table_class_dict()
    session = next(get_db())
    try:
        table_model = table_class_dict.get(catalog_name)
        if not table_model:
            return {"result": "error", "message": f"Table {catalog_name} not found"}
        query = insert(table_model).values(data)
        session.execute(query)
        session.commit()
        return {"result": "ok"}
    except SQLAlchemyError as e:
        session.rollback()
        return {"result": "error", "message": str(e)}
    finally:
        session.close()


def add_test_data():
    session = next(get_db())
    # Добавление данных в Section
    section1 = Section(id=1, title="Секция 1", description="")
    section2 = Section(id=2, title="Секция 2", description="")

    session.add_all([section1, section2])
    session.commit()

    # Добавление данных в IndicatorValueVariety
    variety1 = IndicatorValueVariety(id=1, title="Тип 1", description="Описание Типа 1", section_id=1)
    variety2 = IndicatorValueVariety(id=2, title="Тип 2", description="Описание Типа 2", section_id=2)

    session.add_all([variety1, variety2])
    session.commit()

    # Добавление данных в Indicators
    indicator1 = Indicators(id=1, title="Индикатор 1", value_type_id=1, is_used=True)
    indicator2 = Indicators(id=2, title="Индикатор 2", value_type_id=2, is_used=False)
    indicator3 = Indicators(id=3, title="Индикатор 3", value_type_id=1, is_used=True)

    session.add_all([indicator1, indicator2, indicator3])
    session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    add_test_data()
