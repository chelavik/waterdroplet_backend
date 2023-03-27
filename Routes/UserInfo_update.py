from Database import Databases
from Utils.Hasher import HasherClass
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from fastapi import HTTPException, APIRouter
from starlette.responses import JSONResponse
from Routes.Authorization import unpack_token, BadTokenError

router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()


# ----------------------ROUTES--------------------------

@router.put('/change_password', tags=['user'])
async def change_password(new_password: str, token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        hashed_password = Hasher.get_password_hash(new_password)
        await SQLDatabase.change_password(hashed_password, username, user_type)
        return HTTPException(status_code=200)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.put('/change_email', tags=['user'])
async def change_email(token: Token, new_email: str):
    try:
        username, user_type = unpack_token(token.access_token)
        await SQLDatabase.change_email(new_email, username, user_type)
        return HTTPException(status_code=200)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/user_info', tags=['user'])
async def get_user_info(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        print(username, user_type)
        info = await SQLDatabase.get_user(username, user_type)
        return JSONResponse(info)
    except Databases.BadUserError:
        raise HTTPException(status_code=400, detail='incorrect user for route')
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/user_ipu_info', tags=['user'])
async def get_user_ipus(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        info = await SQLDatabase.get_ipus(username, user_type)
        return JSONResponse(info)
    except Databases.BadUserError:
        raise HTTPException(status_code=400, detail='incorrect user for route')
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/get_business', tags=['business'])
async def get_business(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        info = await SQLDatabase.get_business(username, user_type)
        return JSONResponse(info)
    except Databases.BadUserError:
        raise HTTPException(status_code=400, detail='incorrect user for route')
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
