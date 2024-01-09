import pytest

from sqlalchemy.sql import text

import src.domain.model as model
import src.adapters.repository as repository


pytestmark = pytest.mark.usefixtures("mappers")

def test_repository_can_save_a_batch(sqlite_session_factory):
    session = sqlite_session_factory()
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    repo = repository.SqlAlchemyRepository(session)

    repo.add(batch) 
    session.commit()

    rows = list(session.execute(
    text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"') 
    ))
    assert rows == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(session):
    session.execute( 
        'INSERT INTO order_lines (orderid, sku, qty)'
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )

    [[orderline_id]] = session.execute(
        """SELECT id FROM order_lines WHERE orderid=:orderid AND
        sku=:sku""",
        dict(orderid="order1", sku="GENERIC-SOFA")
    )
    return orderline_id

def insert_batch(session, ref, sku, qty, eta, product_version=1):
    session.execute(
        "INSERT INTO products (sku, version_number) VALUES (:sku, :version)",
        dict(sku=sku, version=product_version),
    )
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES (:ref, :sku, :qty, :eta)",
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )
