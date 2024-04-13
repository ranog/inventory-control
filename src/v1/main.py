from fastapi import FastAPI
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

app = FastAPI()


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
