from fastapi import FastAPI
from src.service import register_part

from src.model import Part

app = FastAPI()


@app.get('/v1/ping/', include_in_schema=False)
async def root():
    return 'pong'


@app.post('/v1/parts/')
async def create_part(part: Part):
    return await register_part(part)
