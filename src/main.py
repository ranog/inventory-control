from fastapi import FastAPI


app = FastAPI()


@app.get('/v1/ping/', include_in_schema=False)
async def root():
    return 'pong'
