from typing import Union

from fastapi import APIRouter, Depends, Request, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.entities.users import UserManager, User


router = APIRouter()


@router.get('/me')
async def me(user: User = Depends(UserManager.get_current_user)):
    return user


@router.get('/all_users')
async def all_users():
    return await UserManager.all_users()


@router.post('/registration')
async def registration(user: User):
    return await UserManager.create_user(user.login, user.pwd)


@router.post('/authenticate')
async def authenticate(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserManager.get_user(form_data.username, form_data.password)

    if user is None:
        raise HTTPException(status_code=400, detail='Incorrect login or password')

    session = await UserManager.create_session(user)
    response = JSONResponse(content='Successfully')
    response.set_cookie(key='session', value=session)
    return response


@router.post('/logout')
async def logout(user: User = Depends(UserManager.get_current_user),
                 session: Union[str, None] = Cookie(default=None),):
    await UserManager.logout(session)

    response = JSONResponse(content='Successfully')
    response.delete_cookie('session')

    return response
