from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.service import part_details, register_part
from src.model import Part

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
async def search_for_part(part_number: int):
    part_data = await part_details(part_number)
    if part_data:
        return part_data
    return JSONResponse(status_code=404, content={'detail': 'Part number not found'})
