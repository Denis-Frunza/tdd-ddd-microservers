import abc
from typing import Set

import src.domain.model as model


class AbstractRepository(abc.ABC):

    @abc.abstractmethod 
    def add(self, batch: model.Batch):
        ...

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        ...


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(
            model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()

class FakeSession():
    committed = False
    def commit(self):
        self.committed = True