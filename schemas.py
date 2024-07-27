from typing import List, Optional
from pydantic import BaseModel


class ColumnInfo(BaseModel):
    name: str
    title: Optional[str] = None
    type: str
    nullable: bool
    foreign_key: dict | None


class TableInfo(BaseModel):
    name: str
    title: Optional[str] = None
    columns: List[ColumnInfo]
