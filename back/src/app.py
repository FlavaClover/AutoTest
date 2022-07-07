from fastapi import FastAPI
from src.routers import auth
from src.db.database import database


app = FastAPI()
app.include_router(auth.router, prefix='/auth', tags=['Auth'])


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()

