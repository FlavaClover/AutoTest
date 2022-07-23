from typing import Union, List
from src.tools.pg_catch_error_decorator import pg_catch_error_decorator
from fastapi import APIRouter, Depends, Request, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import logging
from src.entities.user import UserManager, User


router = APIRouter()
logger = logging.getLogger('api')


@router.get('/me', response_model=User)
@pg_catch_error_decorator
async def me(user: User = Depends()):
    logger.info(user.login + ' me.')
    return user


@router.get('/all_users', response_model=List[User])
@pg_catch_error_decorator
async def all_users():
    return await UserManager.all_users()


@router.post('/registration')
@pg_catch_error_decorator
async def registration(user: User):
    return await UserManager.create_user(user)


@router.post('/authenticate')
@pg_catch_error_decorator
async def authenticate(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserManager.get_user(form_data.username, form_data.password)

    if user is None:
        raise HTTPException(status_code=400, detail='Incorrect login or password')

    session = await UserManager.create_session(user)
    response = JSONResponse(content='Successfully')
    response.set_cookie(key='session', value=session)

    logger.info(user.login + ' successfully authenticated.')
    return response


@router.post('/logout')
@pg_catch_error_decorator
async def logout(user: User = Depends(),
                 session: Union[str, None] = Cookie(default=None),):
    await UserManager.logout(session)

    response = JSONResponse(content='Successfully')
    response.delete_cookie('session')

    return response
