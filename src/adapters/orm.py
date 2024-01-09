import logging

from sqlalchemy.orm import registry, relationship
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date

import src.domain.model as model


logger = logging.getLogger(__name__)

metadata = MetaData()

order_lines = Table(
    'order_lines', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
    Column('orderid', String(255)),
)


products = Table(
    "products",
    metadata,
    Column("sku", String(255), primary_key=True),
    Column("version_number", Integer, nullable=False, server_default="0"),
)


batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", ForeignKey("products.sku")),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)


allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


# Create a registry
mapper_registry = registry()

def start_mappers():
    logger.info("Starting mappers")
    # Use the map_imperatively method of the registry
    mapper_registry.map_imperatively(model.OrderLine, order_lines)
    # Mapping for Batch with relationship
    batches_mapper = mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                model.OrderLine,  # Directly referencing the class instead of lines_mapper
                secondary=allocations,
                collection_class=set,
            )
        },
    )