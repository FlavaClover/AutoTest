from typing import Optional, Union
from fastapi import Cookie, HTTPException, status
import crypt
from src.db.database import DataBase
from src.entities.schemas import User


class UserManager:
    def __init__(self):
        pass

    @classmethod
    async def all_users(cls):
        return await DataBase.select(table='users')

    @classmethod
    async def create_user(cls, user: User):
        salt = crypt.mksalt()
        key = crypt.crypt(user.pwd, salt)

        user = User(login=user.login, pwd=key, salt=salt)

        user.id = await DataBase.insert('users', values=user.dict())

        return user

    @classmethod
    async def get_user(cls, login: str, pwd: str):
        data = await DataBase.select('users', where='login = :login', params={'login': login}, scalar=True)
        if data is None:
            return None
        user = User(**data)
        if crypt.crypt(pwd, user.salt) == user.pwd:
            return user
        else:
            return None

    @classmethod
    async def get_current_user(cls, session: Optional[str] = Cookie(None)):
        data = await DataBase.function('f_get_user_by_session', session=session)

        if data is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        else:
            await DataBase.function('f_update_session', session=session)

        return User(**data)

    @classmethod
    async def create_session(cls, user: Union[User, int]):
        if isinstance(user, int):
            result = await DataBase.function('f_create_session', user_id=user)
        else:
            result = await DataBase.function('f_create_session', user_id=user.id)
        return result.f_create_session

    @classmethod
    async def logout(cls, session: str):
        await DataBase.function('f_cancel_session', session=session)
