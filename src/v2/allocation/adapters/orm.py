from sqlalchemy import MetaData, Column, Integer, Table, String, Date, ForeignKey, create_engine, event
from sqlalchemy.orm import registry, relationship

from src.v2.allocation import config
from src.v2.allocation.domain import model

metadata = MetaData()
registry = registry()

order_lines = Table(
    'order_lines',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
    Column('order_id', String(255)),
)

products = Table(
    'products',
    metadata,
    Column('sku', String(255), primary_key=True),
    Column('version_number', Integer, nullable=False, server_default='0'),
)

batches = Table(
    'batches',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('reference', String(255)),
    Column('sku', ForeignKey('products.sku')),
    Column('_purchased_quantity', Integer, nullable=False),
    Column('eta', Date, nullable=True),
)

allocations = Table(
    'allocations',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('orderline_id', ForeignKey('order_lines.id')),
    Column('batch_id', ForeignKey('batches.id')),
)


def start_mappers():
    lines_mapper = registry.map_imperatively(class_=model.OrderLine, local_table=order_lines)
    batches_mapper = registry.map_imperatively(
        class_=model.Batch,
        local_table=batches,
        properties={
            '_allocations': relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            ),
        },
    )
    registry.map_imperatively(
        class_=model.Product,
        local_table=products,
        properties={'batches': relationship(batches_mapper)},
    )


def create_tables():
    engine = create_engine(config.get_postgres_uri(), pool_pre_ping=True)
    metadata.create_all(engine)
    yield
    engine.dispose()


@event.listens_for(model.Product, 'load')
def receive_load(product, _):
    product.events = []
