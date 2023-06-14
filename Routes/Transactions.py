import numpy
import requests

from Database import Databases
from Utils.Hasher import HasherClass, EncryptionClass
from Utils.QRscanner import scanQR
from jose.exceptions import ExpiredSignatureError
from Models.Models import *
from starlette.responses import JSONResponse
from fastapi import HTTPException, APIRouter, UploadFile, Form, File
from Routes.Authorization import unpack_token, BadTokenError
from Database.Databases import NotFoundError
from config import SECRET_KEY

Database = Databases.DatabaseBaseClass()
router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()
Encrypter = EncryptionClass()


# --------------------FUNCTIONS--------------------

def count_sum(delta_number, tariff):
    return delta_number * tariff


# --------------------ROUTES-----------------------


@router.post('/add_transaction', tags=['transactions'])
async def add_transaction(key: Secret_key, login: str, new_number: str, ipu: str):
    try:
        if not Hasher.verify_password(key.key, SECRET_KEY):
            raise HTTPException(status_code=400, detail='bad secret key')
        user_id, tariff = await SQLDatabase.get_user_id_tariff(login)
        prev_number = await SQLDatabase.get_last_number(user_id, ipu)
        if int(new_number) <= int(prev_number):
            raise HTTPException(status_code=403, detail='new_number is less than previous or its same')
        trans_id = await SQLDatabase.add_transaction(user_id, prev_number, new_number, ipu,
                                                     count_sum(int(new_number) - int(prev_number), tariff))
        return JSONResponse(trans_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')
    except NotFoundError:
        raise HTTPException(status_code=404, detail='ipu not found')


@router.post('/trans_status', tags=['transactions'])
async def change_trans_status(key: Secret_key, token: Token, trans_id: int, status: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if not Hasher.verify_password(key.key, SECRET_KEY):
            raise HTTPException(status_code=403, detail='bad secret key')
        await SQLDatabase.change_status(trans_id, status)
        return HTTPException(status_code=200)
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=400, detail='bad token')


@router.post('/first_ipu_value', tags=['transactions'])
async def add_first_value(key: Secret_key, token: Token, ipu: str, new_number: str):
    try:
        username, user_type = unpack_token(token.access_token)
        if not Hasher.verify_password(key.key, SECRET_KEY):
            raise HTTPException(status_code=403, detail='bad secret key')
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


@router.post('/scan_photo', tags=['test'])
async def scan_photo(photo: UploadFile = File(...), key: str = Form()):
    if not Hasher.verify_password(key, SECRET_KEY):
        raise HTTPException(status_code=403, detail='bad secret key')
    content = await photo.read()
    nparr = numpy.frombuffer(content, numpy.uint8)
    info = scanQR(nparr)
    info = Encrypter.decrypt_qrinfo(info)
    info = info.split(sep='.')  # договор, счетчик
    data = {"token": "apitokentest"}
    files = {"upload_image": (photo.filename, content)}
    print('checking photo...')
    number_result = requests.post(url='http://185.185.70.161:5500/get_number',
                                  data=data, files=files)
    print('photo checked')
    if number_result.status_code == 200:
        res = number_result.json()  # цифры на счетчике
        print('got number,', res)
        print(res['number'], info[1], info[0])
        if res == "":
            raise HTTPException(status_code=404, detail='number not found')
        transaction_result = requests.post(url='http://185.185.70.161:5001/add_transaction',
                                           params={'new_number': res['number'], 'ipu': info[1], 'login': info[0]},
                                           json={"key": SECRET_KEY})
        print('request done')
        if transaction_result.status_code == 200:
            transaction_result = transaction_result.json()
            print(transaction_result)
            return transaction_result
    print('no result')