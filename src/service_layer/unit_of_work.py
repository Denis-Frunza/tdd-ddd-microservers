from __future__ import annotations
from abc import ABC, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from src.adapters import repository
from src.service_layer import message_bus
from src import config


DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
    config.get_postgres_uri(),
    isolation_level="REPEATABLE READ",
))


class UnitOfWork(ABC):
    products: repository.AbstractRepository

    @abstractmethod
    def rollback(self):
        ...
    
    @abstractmethod
    def  commit(self):
        ...


    def __enter__(self) -> UnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(self.session)

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
