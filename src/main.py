from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.service import register_part
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
