from Database import Databases
from Utils.Hasher import HasherClass
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from starlette.responses import JSONResponse
from fastapi import HTTPException, APIRouter
from Routes.Authorization import unpack_token, BadTokenError
from Database.Databases import NotFoundError
from config import SECRET_KEY

Database = Databases.DatabaseBaseClass()
router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()


# --------------------FUNCTIONS--------------------

def count_sum(delta_number, tariff):
    return delta_number * tariff


# --------------------ROUTES-----------------------


@router.post('/add_transaction', tags=['transactions'])
async def add_transaction(key: Secret_key, token: Token, new_number: str, ipu: str):
    try:
        if Hasher.get_password_hash(Secret_key.key) != SECRET_KEY:
            raise HTTPException(status_code=403, detail='bad secret key')
        username, user_type = unpack_token(token.access_token)
        user_id, tariff = await SQLDatabase.get_user_id_tariff(username)
        prev_number = await SQLDatabase.get_last_number(user_id, ipu)
        trans_id = await SQLDatabase.add_transaction(user_id, prev_number, new_number, ipu,
                                                     count_sum(int(new_number) - int(prev_number), tariff))
        return JSONResponse(trans_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/trans_status', tags=['transactions'])
async def change_trans_status(key: Secret_key, token: Token, trans_id: int, status: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if Hasher.get_password_hash(Secret_key.key) != SECRET_KEY:
            raise HTTPException(status_code=403, detail='bad secret key')
        await SQLDatabase.change_status(trans_id, status)
        return HTTPException(status_code=200)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/first_ipu_value', tags=['transactions'])
async def add_first_value(token: Token, ipu: str, new_number: str):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == 'physic':
            await SQLDatabase.first_value(username, ipu, new_number)
            return HTTPException(status_code=200, detail='success')
        else:
            raise HTTPException(status_code=403, detail='bad user_type')
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
    except NotFoundError:
        raise HTTPException(status_code=404, detail='ipu not found')
