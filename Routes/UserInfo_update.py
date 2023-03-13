from Database import Databases
from Utils.Hasher import HasherClass, SECRET_KEY, ALGORITHM
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from fastapi import HTTPException, Depends, APIRouter, status
from Routes.Authorization import unpack_token, BadTokenError

Database = Databases.DatabaseBaseClass()
router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()


# ----------------------ROUTES--------------------------

@router.put('/change_password', tags=['user'])
async def change_password(token: Token, new_password: str):
    try:
        username, user_type = unpack_token(token.access_token)
        hashed_password = Hasher.get_password_hash(new_password)
        await SQLDatabase.change_password(hashed_password, username, user_type)
    except ExpiredSignatureError:
        return HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')


@router.put('/change_email', tags=['user'])
async def change_email(token: Token, new_email: str):
    try:
        username, user_type = unpack_token(token.access_token)
        await SQLDatabase.change_email(new_email, username, user_type)
    except ExpiredSignatureError:
        return HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')


@router.post('/user_info', tags=['user'])
async def get_user_info(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        info = await SQLDatabase.get_user(username, user_type)
        return info
    except Databases.BadUserError:
        return HTTPException(status_code=400, detail='incorrect user for route')
    except ExpiredSignatureError:
        return HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        return HTTPException(status_code=400, detail='bad token')
