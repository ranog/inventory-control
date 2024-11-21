from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.v1.service import (
    delete_part_record,
    list_parts,
    part_details,
    register_part,
    update_part,
)
from src.v1.model import Part
from src.v2.allocation.adapters import orm
from src.v2.allocation.service_layer import services, unit_of_work


@asynccontextmanager
async def lifespan(app: FastAPI):
    orm.start_mappers()
    orm.create_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post('/v2/allocations', status_code=201)
async def allocations_endpoint(request: Request):
    body = await request.json()
    try:
        batch_ref = services.allocate(
            order_id=body['order_id'],
            sku=body['sku'],
            qty=body['qty'],
            uow=unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except services.InvalidSku as e:
        return JSONResponse(status_code=400, content={'message': str(e)})
    return {'batch_ref': batch_ref}


@app.post('/v2/batches', status_code=201)
async def batches_endpoint(request: Request):
    body = await request.json()
    eta = body['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        ref=body['ref'],
        sku=body['sku'],
        qty=body['qty'],
        eta=eta,
        uow=unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return {'message': 'OK'}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, error):
    return JSONResponse(
        status_code=400,
        content={'detail': 'Validation error', 'errors': error.errors()},
    )


@app.get('/v1/ping/', include_in_schema=False)
async def root():
    return 'pong'


@app.post('/v1/parts/')
async def create_part(part: Part):
    return await register_part(part)


@app.get('/v1/parts/{part_number}')
async def search_part_by_number(part_number: int):
    part_data = await part_details(part_number)
    if part_data:
        return part_data
    return JSONResponse(status_code=404, content={'detail': 'Part number not found'})


@app.get('/v1/parts/')
async def find_all_parts():
    return await list_parts()


@app.put('/v1/parts/{part_number}')
async def update_part_registration(part_number: int, data_to_update: dict):
    return await update_part(part_number=part_number, data_to_update=data_to_update)


@app.delete('/v1/parts/{part_number}')
async def delete_part(part_number: int):
    part_data = await part_details(part_number)
    if part_data:
        return await delete_part_record(part_number)
    return JSONResponse(status_code=404, content={'detail': 'Part number not found'})
