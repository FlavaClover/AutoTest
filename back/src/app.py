from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.entities.user import User, UserManager
from src.routers import auth, problem
from src.db.database import DataBase
import configparser

config = configparser.ConfigParser()
config.read('configs/config.ini')
DataBase.set_settings(config['Database']['DATABASE_URL'])

app = FastAPI()
app.include_router(auth.router, prefix='/auth', tags=['Auth'])
app.include_router(problem.router, prefix='/problem', tags=['Problem'])
app.dependency_overrides[User] = UserManager.get_current_user

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie"],
)


@app.on_event('startup')
async def startup():
    await DataBase.connect()


@app.on_event('shutdown')
async def shutdown():
    await DataBase.disconnect()

