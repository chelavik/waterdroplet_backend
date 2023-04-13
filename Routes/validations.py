from Database import Databases
from Database.Databases import NotFoundError
from Utils.Hasher import HasherClass
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from fastapi import HTTPException, APIRouter
from starlette.responses import JSONResponse
from Routes.Authorization import unpack_token, BadTokenError

router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()


@router.post('/get_related_physics', tags=['business'])
async def get_related_physics(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            info = await SQLDatabase.get_related_physics(username)
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_related_physics/{page_id}', tags=['business'])
async def get_hundred_physics(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            page_id -= 1
            info = await SQLDatabase.get_hundred_physics(username, page_id)
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/suspicious_validations/{page_id}', tags=['business'])
async def get_suspicious_validations(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            info = await SQLDatabase.get_suspicious_validations(username, page_id)
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_related_address/{page_id}', tags=['sotrudnik'])
async def get_related_address(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "sotrudnik":
            page_id -= 1
            info = await SQLDatabase.get_addresses(username, page_id)
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_ipus_by_address', tags=['sotrudnik'])
async def get_ipus_by_address(token: Token, address: str):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "sotrudnik":
            info = await SQLDatabase.get_ipus_by_address(address)
            output = info['ipus'].split()
            return JSONResponse(output)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/new_validation', tags=['sotrudnik'])
async def new_validation(token: Token, sotr_number: int, ipu: str, address: str):
    try:
        username, user_type = unpack_token(token.access_token)
        if not user_type == "sotrudnik":
            raise HTTPException(status_code=400, detail="bad user_type")
        await SQLDatabase.add_validation(username, sotr_number, ipu, address)
        return HTTPException(status_code=200, detail="success")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_validation_logs', tags=['transactions'])
async def get_validation_logs(token: Token, validation_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type != 'business':
            raise HTTPException(status_code=403, detail='bad user_type')
        data = SQLDatabase.get_validation_logs(username, validation_id)
        return JSONResponse(data)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
    except NotFoundError:
        raise HTTPException(status_code=404, detail='validation not found')