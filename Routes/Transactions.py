from Database import Databases
from Utils.Hasher import HasherClass
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from starlette.responses import JSONResponse
from fastapi import HTTPException, APIRouter
from Routes.Authorization import unpack_token, BadTokenError

Database = Databases.DatabaseBaseClass()
router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()


# --------------------FUNCTIONS--------------------

def count_sum(delta_number, tariff):
    return delta_number * tariff


# --------------------ROUTES-----------------------


@router.post('/add_transaction', tags=['transactions'])
async def add_transaction(token: Token, new_number: str, ipu: str):
    try:
        username, user_type = unpack_token(token.access_token)
        user_id, tariff = SQLDatabase.get_user_id_tariff(username)
        prev_number = await SQLDatabase.get_last_number(user_id, ipu)
        trans_id = await SQLDatabase.add_transaction(user_id, prev_number, new_number, ipu,
                                                     count_sum(int(new_number) - int(prev_number), tariff))
        return JSONResponse(trans_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/trans_status', tags=['transactions'])
async def change_trans_status(token: Token, trans_id: int, status: int):
    try:
        username, user_type = unpack_token(token.access_token)
        await SQLDatabase.change_status(trans_id, status)
        return HTTPException(status_code=200)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
