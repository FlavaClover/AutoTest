from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.entities.users import UserManager, User


router = APIRouter()


@router.get('/me')
async def me(user: User = Depends(UserManager.get_current_user)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


@router.get('/all_users')
async def all_users():
    return await UserManager.all_users()


@router.post('/registration')
async def registration(user: User):
    return await UserManager.create_user(user.login, user.pwd)


@router.post('/auth')
async def authenticate(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserManager.get_user(form_data.username, form_data.password)

    if user is None:
        raise HTTPException(status_code=400, detail='Incorrect login or password')

    response = JSONResponse(user.__dict__)
    response.set_cookie(key='session', value='session1')
    return response

