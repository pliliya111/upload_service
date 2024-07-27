from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeMeta, relationship
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic

from convert_pydantic import get_pydantic_dto_schema_by_sqlalchemy_model

Base = declarative_base()


class Advice(Base):
    __tablename__ = 'advices_d'
    __table_args__ = {'info': {'type': 'dynamic'}, "comment": "Советы"}

    id = Column(Integer, primary_key=True, comment="Идентификатор")
    dt = Column(
        DateTime,
        server_default=func.timezone(
            func.current_setting("TIMEZONE"), func.date_trunc("second", func.now())
        ),
        nullable=False,
        comment="Дата и время записи",
        index=True,
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def get_schema():
        """Схема для валидации запросов на вставку и редактирование"""
        schema = get_pydantic_dto_schema_by_sqlalchemy_model(Advice, exclude=['id'])
        return schema


class Section(Base):
    __tablename__ = 'section'
    __table_args__ = {'info': {'type': 'reference'}, "comment": "Секция"}

    id = Column(Integer, primary_key=True, comment="Идентификатор")
    title = Column(String, nullable=False, comment="Заголовок")
    description = Column(String, comment="Описание")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def get_schema():
        """Схема для валидации запросов на вставку и редактирование"""
        schema = get_pydantic_dto_schema_by_sqlalchemy_model(Section, exclude=['id'])
        return schema


class IndicatorValueVariety(Base):
    __tablename__ = 'indicator_types'
    __table_args__ = {'info': {'type': 'reference'}, "comment": "Тип индикатора"}

    id = Column(Integer, primary_key=True, comment="Идентификатор")
    title = Column(String, nullable=False, comment="Заголовок")
    description = Column(String, comment="Описание")
    section_id = Column(
        Integer,
        ForeignKey(
            Section.id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="Секция",
    )
    def as_dict(self):
        res = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return res

    @staticmethod
    def get_schema():
        """Схема для валидации запросов на вставку и редактирование"""
        schema = get_pydantic_dto_schema_by_sqlalchemy_model(IndicatorValueVariety, exclude=['id'])
        return schema


class Indicators(Base):
    __tablename__ = 'indicators'
    __table_args__ = {'info': {'type': 'reference'}, "comment": "Индикаторы"}

    id = Column(Integer, primary_key=True, comment="Идентификатор")
    title = Column(String, nullable=False, comment="Заголовок")
    value_type_id = Column(
        Integer,
        ForeignKey(
            IndicatorValueVariety.id,
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="Тип",
    )
    is_used = Column(Boolean, comment="Используется на интерфейсе")
    value_type = relationship(IndicatorValueVariety, backref='indicators', lazy=True)

    @hybrid_property
    def section_id(self):
        return self.value_type.section_id

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data['section_id'] = self.section_id
        return data

    @staticmethod
    def get_schema():
        """Схема для валидации запросов на вставку и редактирование"""
        schema = get_pydantic_dto_schema_by_sqlalchemy_model(Indicators, exclude=['id'])
        return schema
