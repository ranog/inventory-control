import uuid
from datetime import date

import pytest

from src import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=''):
    return f'sku-{name}-{random_suffix()}'


def random_batch_ref(name=''):
    return f'batch-{name}-{random_suffix()}'


def random_order_id(name=''):
    return f'order-{name}-{random_suffix()}'


def post_to_add_batch(test_client, ref: str, sku: str, qty: int, eta: str = None):
    url = config.get_api_url()

    response = test_client.post(f'{url}/v2/batches', json={'ref': ref, 'sku': sku, 'qty': qty, 'eta': eta})

    assert response.status_code == 201


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch(test_client):
    sku, other_sku = random_sku(), random_sku('other')
    early_batch = random_batch_ref('1')
    later_batch = random_batch_ref('2')
    other_batch = random_batch_ref('3')

    post_to_add_batch(ref=early_batch, sku=sku, qty=100, test_client=test_client)
    post_to_add_batch(ref=later_batch, sku=sku, qty=100, eta=f'{date.today()}', test_client=test_client)
    post_to_add_batch(ref=other_batch, sku=other_sku, qty=100, test_client=test_client)

    data = {'order_id': random_order_id(), 'sku': sku, 'qty': 3}
    url = config.get_api_url()

    response = test_client.post(f'{url}/v2/allocations', json=data)

    assert response.status_code == 201
    assert response.json()['batch_ref'] == early_batch


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message(test_client):
    unknown_sku, order_id = random_sku(), random_order_id()
    data = {'order_id': order_id, 'sku': unknown_sku, 'qty': 3}
    url = config.get_api_url()

    response = test_client.post(f'{url}/v2/allocations', json=data)

    assert response.status_code == 400
    assert response.json()['message'] == f'Invalid sku {unknown_sku}'
