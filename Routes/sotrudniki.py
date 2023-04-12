from Database import Databases
from Database.Databases import NotFoundError, BadUserError, BadUsernameError
from Utils.Hasher import HasherClass
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from fastapi import HTTPException, APIRouter
from starlette.responses import JSONResponse
from Routes.Authorization import unpack_token, BadTokenError


router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()


# -----------------ROUTES--------------------

@router.post('/workers/get_all_workers', tags=['workers'])
async def get_all_workers(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            info = await SQLDatabase.get_all_workers(username)
            return JSONResponse({info})
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/workers/worker_info/{worker_id}', tags=['workers'])
async def get_worker_info(token: Token, worker_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            info = await SQLDatabase.get_worker_info(username, worker_id)
            return JSONResponse({'worker': info})
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except NotFoundError:
        raise HTTPException(status_code=404, detail='worker not found or not related to this business')
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.delete('/workers/delete_worker/{worker_id}', tags=['workers'])
async def delete_worker(token: Token, worker_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            await SQLDatabase.delete_worker(username, worker_id)
            return HTTPException(status_code=200)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except NotFoundError:
        raise HTTPException(status_code=404, detail='worker not found')
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/workers/create_worker', tags=['workers'])
async def create_worker(token: Token, worker: Worker):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            await SQLDatabase.create_worker(username, worker.login, worker.phone, worker.password)
            return HTTPException(status_code=200)
        else:
            raise HTTPException(status_code=402, detail="bad user_type")
    except NotFoundError:
        raise HTTPException(status_code=404, detail='worker not found')
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')
    except BadUserError:
        raise HTTPException(status_code=402, detail="username occupied")


@router.put('/workers/edit_login/{worker_id}', tags=['workers'])
async def edit_worker_login(token: Token, worker_id: int, login: str):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            await SQLDatabase.edit_worker_login(username, worker_id, login)
            return HTTPException(status_code=200)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except NotFoundError:
        raise HTTPException(status_code=404, detail='worker not found')
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
    except BadUsernameError:
        raise HTTPException(status_code=402, detail="username occupied")


@router.put('/workers/edit_phone/{worker_id}', tags=['workers'])
async def edit_worker_phone(token: Token, worker_id: int, phone: str):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            await SQLDatabase.edit_worker_phone(username, worker_id, phone)
            return HTTPException(status_code=200)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except NotFoundError:
        raise HTTPException(status_code=404, detail='worker not found')
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.put('/workers/edit_password/{worker_id}', tags=['workers'])
async def edit_worker_password(token: Token, worker_id: int, password: str):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            await SQLDatabase.edit_worker_password(username, worker_id, password)
            return HTTPException(status_code=200)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except NotFoundError:
        raise HTTPException(status_code=404, detail='worker not found')
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')




