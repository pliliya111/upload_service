from typing import Container, Optional, Type
from urllib.error import HTTPError

from pydantic import BaseModel, ConfigDict, create_model
from sqlalchemy.ext.hybrid import hybrid_property

orm_config = ConfigDict(from_attributes=True)


def get_pydantic_dto_schema_by_sqlalchemy_model(
        model,
        config=orm_config,
        exclude: list[str] | None = None,
        all_nullable: bool = False,
) -> BaseModel:
    """
    Получить схему валидации на основе данных модели sqlalchemy.

    :return: схема валидации pydantic.
    """
    print('=====')
    if exclude is None:
        exclude = []

    fields = {}
    for column in model.columns:
        name = column.name
        if name in exclude:
            continue
        python_type: type | None = None
        if hasattr(column.type, "impl"):
            if hasattr(column.type.impl, "python_type"):
                python_type = column.type.impl.python_type
        elif hasattr(column.type, "python_type"):
            python_type = column.type.python_type

        if python_type is None:
            raise HTTPError(
                message=f"Ошибка генерации валидатора pydantic из модели sqlalchemy из-за колонки {name}"
            )

        if all_nullable or column.nullable:
            fields[name] = (python_type | None, None)
        else:
            fields[name] = (python_type, ...)

    pydantic_dto_schema = create_model(
        model.name,
        __config__=config,
        **fields,
    )
    print(pydantic_dto_schema)
    return pydantic_dto_schema
