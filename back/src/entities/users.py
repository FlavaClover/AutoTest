import datetime
from typing import Optional

from fastapi import Cookie

from src.db.database import DataBase
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int]
    login: str
    pwd: str
    last_login: Optional[datetime.datetime]


class UserManager:
    def __init__(self):
        pass

    @classmethod
    async def all_users(cls):
        return await DataBase.select(table='users')

    @classmethod
    async def create_user(cls, login: str, pwd: str):
        return await DataBase.function('f_add_user', login=login, pwd=pwd)

    @classmethod
    async def get_user(cls, login: str, pwd: str):
        data = await DataBase.function('f_get_user', login=login, pwd=pwd)
        if data is None:
            return None
        else:
            return User(**data)

    @classmethod
    async def get_current_user(cls, session: Optional[str] = Cookie(None)):
        print(session)
        if session is None:
            return None
        return User(login='current', pwd='pwd')