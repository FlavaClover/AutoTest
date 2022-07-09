from fastapi import FastAPI
from src.entities.user import User, UserManager
from src.routers import auth
from src.db.database import database


app = FastAPI()
app.include_router(auth.router, prefix='/auth', tags=['Auth'])
app.dependency_overrides[User] = UserManager.get_current_user


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()

