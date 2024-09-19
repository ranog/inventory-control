import uuid

import pytest

from src.v2.allocation import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=''):
    return f'sku-{name}-{random_suffix()}'


def random_batch_ref(name=''):
    return f'batch-{name}-{random_suffix()}'


def random_order_id(name=''):
    return f'order-{name}-{random_suffix()}'


@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch(add_stock, test_client):
    sku, other_sku = random_sku(), random_sku('other')
    early_batch = random_batch_ref('1')
    later_batch = random_batch_ref('2')
    other_batch = random_batch_ref('3')
    add_stock(
        [
            (later_batch, sku, 100, '2011-01-02'),
            (early_batch, sku, 100, '2011-01-01'),
            (other_batch, other_sku, 100, None),
        ]
    )
    data = {'order_id': random_order_id(), 'sku': sku, 'qty': 3}
    url = config.get_api_url()

    response = test_client.post(f'{url}/v2/allocate', json=data)

    assert response.status_code == 201
    assert response.json()['batch_ref'] == early_batch


@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message(add_stock, test_client):
    unknown_sku, order_id = random_sku(), random_order_id()
    add_stock([])
    data = {'order_id': order_id, 'sku': unknown_sku, 'qty': 3}
    url = config.get_api_url()

    response = test_client.post(f'{url}/v2/allocate', json=data)

    assert response.status_code == 400
    assert response.json()['message'] == f'Invalid sku {unknown_sku}'
