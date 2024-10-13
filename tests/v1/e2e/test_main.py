from httpx import AsyncClient
from src.v1.service import list_parts, part_details


async def test_it_should_ping_successfully(async_http_client: AsyncClient):
    response = await async_http_client.get('/v1/ping/')

    assert response.status_code == 200
    assert response.json() == 'pong'


async def test_it_should_register_part(async_http_client: AsyncClient, part_payload: dict):
    response = await async_http_client.post('/v1/parts/', json=part_payload)

    expected_result = await part_details(response.json()['part_number'])

    assert response.status_code == 200
    assert part_payload['name'] == expected_result.name
    assert part_payload['quantity'] == expected_result.quantity
    assert part_payload['description'] == expected_result.description


async def test_it_should_return_400_when_registering_part_with_invalid_payload(
    async_http_client: AsyncClient,
    part_payload: dict,
):
    part_payload.pop('description')
    expected_error = [
        {
            'input': {
                'name': 'Stepper motor',
                'quantity': 100,
            },
            'loc': ['body', 'description'],
            'msg': 'Field required',
            'type': 'missing',
        },
    ]

    response = await async_http_client.post('/v1/parts/', json=part_payload)

    assert response.status_code == 400
    assert response.json()['errors'] == expected_error


async def test_it_should_return_part_details(async_http_client: AsyncClient, part_payload: dict):
    response = await async_http_client.post('/v1/parts/', json=part_payload)

    part_number = response.json()['part_number']
    expected_result = await part_details(part_number)

    response = await async_http_client.get(f'/v1/parts/{part_number}')

    assert response.status_code == 200
    assert response.json() == expected_result.dict()


async def test_it_should_return_404_when_getting_part_details_with_invalid_part_number(
    async_http_client: AsyncClient,
):
    response = await async_http_client.get(f'/v1/parts/{999}')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Part number not found'}


async def test_it_should_return_all_parts_registered(async_http_client: AsyncClient, parts_to_register: list[dict]):
    for part_data in parts_to_register:
        await async_http_client.post('/v1/parts/', json=part_data)

    expected_result = await list_parts()

    response = await async_http_client.get('/v1/parts/')

    assert response.status_code == 200
    assert response.json() == expected_result


async def test_it_should_return_empty_list_when_no_parts_registered(
    async_http_client: AsyncClient,
):
    response = await async_http_client.get('/v1/parts/')

    assert response.status_code == 200
    assert response.json() == []


async def test_it_should_update_part(async_http_client: AsyncClient, part_payload: dict, updated_part_payload: dict):
    response = await async_http_client.post('/v1/parts/', json=part_payload)
    part_number = response.json()['part_number']

    response = await async_http_client.put(f'/v1/parts/{part_number}', json=updated_part_payload)

    expected_result = await part_details(part_number)

    assert response.status_code == 200
    assert updated_part_payload['name'] == expected_result.name
    assert updated_part_payload['quantity'] == expected_result.quantity
    assert updated_part_payload['description'] == expected_result.description


async def test_it_should_update_part_with_partial_data(async_http_client: AsyncClient, part_payload: dict):
    response = await async_http_client.post('/v1/parts/', json=part_payload)
    part_number = response.json()['part_number']
    updated_part_payload = {'name': 'DC motor'}

    await async_http_client.put(f'/v1/parts/{part_number}', json=updated_part_payload)

    expected_result = await part_details(part_number)

    assert updated_part_payload['name'] == expected_result.name
    assert part_payload['quantity'] == expected_result.quantity
    assert part_payload['description'] == expected_result.description


async def test_it_should_delete_the_record_from_the_database(async_http_client: AsyncClient, part_payload: dict):
    response = await async_http_client.post('/v1/parts/', json=part_payload)
    part_number = response.json()['part_number']

    response = await async_http_client.delete(f'/v1/parts/{part_number}')

    assert response.status_code == 200
    assert await part_details(part_number) is None


async def test_it_should_return_404_when_deleting_part_with_invalid_part_number(
    async_http_client: AsyncClient,
):
    response = await async_http_client.delete(f'/v1/parts/{999}')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Part number not found'}
