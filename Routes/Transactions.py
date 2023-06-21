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
from Database.Databases import NotFoundError, BadIpuDeltaError
from config import SECRET_KEY, iputoken
from cryptography.fernet import InvalidToken

Database = Databases.DatabaseBaseClass()
router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()
Encrypter = EncryptionClass()


# --------------------FUNCTIONS--------------------

def count_sum(delta_number, tariff):
    return delta_number * tariff


headers = requests.utils.default_headers()

headers.update(
    {
        'User-Agent': 'My User Agent 1.0',
    }
)


async def add_transaction(key: str, login: str, new_number: str, ipu: str):
    try:
        if not Hasher.verify_password(key, SECRET_KEY):
            raise HTTPException(status_code=400, detail='bad secret key')
        user_id, tariff = await SQLDatabase.get_user_id_tariff(login)
        prev_number = await SQLDatabase.get_last_number(user_id, ipu)
        if int(new_number) <= int(prev_number):
            raise BadIpuDeltaError
        trans_id = await SQLDatabase.add_transaction(user_id, prev_number, new_number, ipu,
                                                     count_sum(int(new_number) - int(prev_number), tariff))
        trans_id['first_value'] = False
        return JSONResponse(trans_id)
    except NotFoundError:
        trans_id = await SQLDatabase.first_value(login, ipu, new_number)
        trans_id['first_value'] = True
        return JSONResponse(trans_id)

# --------------------ROUTES-----------------------

@router.post('/trans_status', tags=['transactions'])
async def change_trans_status(key: Secret_key, trans_id: int, status: int):
    try:
        if not Hasher.verify_password(key.key, SECRET_KEY):
            raise HTTPException(status_code=403, detail='bad secret key')
        await SQLDatabase.change_status(trans_id, status)
        return HTTPException(status_code=200)
    except:
        raise HTTPException(status_code=500, detail='Server Error')

@router.post('/trans_status', tags=['transactions'])
async def change_trans_status(key: Secret_key, trans_id: int, status: int):
    try:
        if not Hasher.verify_password(key.key, SECRET_KEY):
            raise HTTPException(status_code=403, detail='bad secret key')
        await SQLDatabase.change_status(trans_id, status)
        return HTTPException(status_code=200)
    except:
        raise HTTPException(status_code=500, detail='Server Error')

@router.post('/scan_photo', tags=['test'])
async def scan_photo(photo: UploadFile = File(...), key: str = Form()):
    if not Hasher.verify_password(key, SECRET_KEY):
        raise HTTPException(status_code=403, detail='bad secret key')
    content = await photo.read()
    qr_info = scanQR(content)
    if qr_info == '':
        raise HTTPException(status_code=404, detail='QR-code not found on photo')
    try:
        info = Encrypter.decrypt_qrinfo(qr_info).split(sep='.')  # договор, счетчик
    except InvalidToken:
        raise HTTPException(status_code=404, detail='QR-code wrong info')
    data = {"token": iputoken}
    files = {"upload_image": (photo.filename, content)}
    number_result = requests.post(url='https://api.waterdroplet.ru/get_number',
                                  data=data, files=files)
    if number_result.status_code == 200:
        res = number_result.json()  # цифры на счетчике
        if res == "":
            raise HTTPException(status_code=417, detail='number not found on photo')
        try:
            trans_id = await add_transaction(key=SECRET_KEY, login=info[0], new_number=res['number'], ipu=info[1])
            return trans_id
        except BadIpuDeltaError:
            raise HTTPException(status_code=417, detail='New value is less than previous or its same')
    else:
        raise HTTPException(status_code=500, detail='API service Error')
