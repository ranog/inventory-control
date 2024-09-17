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
def test_api_returns_allocation(add_stock, test_client):
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
def test_allocations_are_persisted(add_stock, test_client):
    sku = random_sku()
    batch1, batch2 = random_batch_ref('1'), random_batch_ref('2')
    order1, order2 = random_order_id('1'), random_order_id('2')
    add_stock(
        [
            (batch1, sku, 10, '2011-01-01'),
            (batch2, sku, 10, '2011-01-02'),
        ]
    )
    line1 = {'order_id': order1, 'sku': sku, 'qty': 10}
    line2 = {'order_id': order2, 'sku': sku, 'qty': 10}
    url = config.get_api_url()

    response = test_client.post(f'{url}/v2/allocate/', json=line1)

    assert response.status_code == 201
    assert response.json()['batch_ref'] == batch1

    response = test_client.post(f'{url}/v2/allocate/', json=line2)

    assert response.status_code == 201
    assert response.json()['batch_ref'] == batch2


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_out_of_stock(add_stock, test_client):
    sku, small_batch, large_order = random_sku(), random_batch_ref(), random_order_id()
    add_stock([(small_batch, sku, 10, '2011-01-01')])
    data = {'order_id': large_order, 'sku': sku, 'qty': 20}
    url = config.get_api_url()

    response = test_client.post(f'{url}/v2/allocate', json=data)

    assert response.status_code == 400
    assert response.json()['message'] == f'Out of stock for sku {sku}'


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_invalid_sku(test_client, add_stock):
    unknown_sku, order_id = random_sku(), random_order_id()
    add_stock([])
    data = {'order_id': order_id, 'sku': unknown_sku, 'qty': 20}
    url = config.get_api_url()

    response = test_client.post(f'{url}/v2/allocate', json=data)

    assert response.status_code == 400
    assert response.json()['message'] == f'Invalid sku {unknown_sku}'
