from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from Utils.Hasher import *
from Models.Models import *
from Database import Databases
from jose import JWTError, jwt


router = APIRouter()
Hasher = HasherClass()
database = Databases.DatabaseBaseClass()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str):
    # проверка существования в бд и получение пользака
    hashed_password = 'полученный от него хеш из бд'
    if not Hasher.verify_password(password, hashed_password):
        return False
    return "вся необходимая информация о пользователе"


# -----------------------ROUTES----------------------------

@router.post('/register')
async def registration(user: User):
    # проверка существования по username
    # создание пользователя в бд
    return HTTPException(status_code=200, detail='Success')


@router.post('/login')
async def login(user: User):
    if authenticate_user(user.username, user.password):
        pass
        # запись времени входа в бд
        # создание и возврат токена
    else:
        return HTTPException(status_code=400, detail='Invalid login or password')

