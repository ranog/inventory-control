from datetime import date

import pytest
import requests

from src.v2.allocation import config
from tests.v2.conftest import random_sku, random_batch_ref, random_order_id


def post_to_add_batch(ref: str, sku: str, qty: int, eta: str = None):
    url = config.get_api_url()

    response = requests.post(f'{url}/v2/batches', json={'ref': ref, 'sku': sku, 'qty': qty, 'eta': eta})

    assert response.status_code == 201


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch():
    sku, other_sku = random_sku(), random_sku('other')
    early_batch = random_batch_ref('1')
    later_batch = random_batch_ref('2')
    other_batch = random_batch_ref('3')

    post_to_add_batch(ref=early_batch, sku=sku, qty=100)
    post_to_add_batch(ref=later_batch, sku=sku, qty=100, eta=f'{date.today()}')
    post_to_add_batch(ref=other_batch, sku=other_sku, qty=100)

    data = {'order_id': random_order_id(), 'sku': sku, 'qty': 3}
    url = config.get_api_url()

    response = requests.post(f'{url}/v2/allocations', json=data)

    assert response.status_code == 201
    assert response.json()['batch_ref'] == early_batch


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_order_id()
    data = {'order_id': order_id, 'sku': unknown_sku, 'qty': 3}
    url = config.get_api_url()

    response = requests.post(f'{url}/v2/allocations', json=data)

    assert response.status_code == 400
    assert response.json()['message'] == f'Invalid sku {unknown_sku}'
