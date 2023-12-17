import abc

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


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession():
    committed = False
    def commit(self):
        self.committed = True