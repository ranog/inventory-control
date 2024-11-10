import time
import uuid
from pathlib import Path

import requests
from requests.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from src.v2.allocation import config
from src.v2.allocation.adapters.orm import metadata, start_mappers


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=''):
    return f'sku-{name}-{random_suffix()}'


def random_batch_ref(name=''):
    return f'batch-{name}-{random_suffix()}'


def random_order_id(name=''):
    return f'order-{name}-{random_suffix()}'


@pytest.fixture
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    clear_mappers()
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def session(session_factory):
    return session_factory()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail('Postgres never came up')


@pytest.fixture(scope='session')
def postgres_db():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db):
    clear_mappers()
    start_mappers()
    yield sessionmaker(bind=postgres_db)
    clear_mappers()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail('API never came up')


@pytest.fixture
def restart_api():
    app_file_path = Path(__file__).parent.parent.parent / 'src' / 'main.py'
    app_file_path.touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
