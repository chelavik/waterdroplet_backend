import random
import requests

from cryptography.fernet import InvalidToken
from fastapi import HTTPException, APIRouter, UploadFile, Form, File
from fastapi.responses import FileResponse
from jose.exceptions import ExpiredSignatureError
from openpyxl import Workbook
from starlette.responses import JSONResponse

from Database import Databases
from Database.Databases import NotFoundError, BadIpuDeltaError
from Models.Models import *
from Routes.Authorization import unpack_token, BadTokenError
from Utils.Hasher import HasherClass, EncryptionClass
from Utils.QRscanner import scanQR
from config import SECRET_KEY, iputoken

Database = Databases.DatabaseBaseClass()
router = APIRouter()
Hasher = HasherClass()
SQLDatabase = Databases.SQLDatabase()
Encrypter = EncryptionClass()


# --------------------FUNCTIONS--------------------

def count_sum(delta_number, tariff):
    return delta_number * tariff


async def set_verdict(user_id: int, ipu: str):
    # info = await SQLDatabase.get_last_values(user_id, ipu)
    # Делаем умный подсчет с помощью мат. модели
    # возврат 1 или 0
    return random.randint(0, 1)


headers = requests.utils.default_headers()

headers.update(
    {
        'User-Agent': 'My User Agent 1.0',
    }
)


async def add_transaction(key: str, login: str, new_number: str, ipu: str):
    try:
        user_id, tariff = await SQLDatabase.get_user_id_tariff(login)
        prev_number = await SQLDatabase.get_last_number(user_id, ipu)
        if int(new_number) <= int(prev_number):
            if int(new_number) != int(prev_number) or not Hasher.verify_password(key, SECRET_KEY):
                raise BadIpuDeltaError
        trans_id = await SQLDatabase.add_transaction(user_id, prev_number, new_number, ipu,
                                                     count_sum(int(new_number) - int(prev_number) / 1000,
                                                               tariff, set_verdict(user_id, ipu)))
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


@router.post('/scan_photo', tags=['transactions'])
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
            info = await add_transaction(key=key, login=info[0], new_number=res['number'], ipu=info[1])
            return info
        except BadIpuDeltaError:
            raise HTTPException(status_code=417, detail='New value is less than previous or its same')
    else:
        raise HTTPException(status_code=500, detail='API service Error')


@router.post('/get_transactions_logs/{page_id}', tags=['transactions'])
async def get_transactions_logs(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            page_id -= 1
            info = await SQLDatabase.get_transactions_logs(username, page_id)
            for dictionary in info:
                dictionary['transaction_date'] = str(dictionary['transaction_date'])
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/get_suspicious_transactions_logs/{page_id}', tags=['transactions'])
async def get_suspicious_transactions_logs(token: Token, page_id: int):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            page_id -= 1
            info = await SQLDatabase.get_sus_transactions_logs(username, page_id)
            for dictionary in info:
                dictionary['transaction_date'] = str(dictionary['transaction_date'])
            return JSONResponse(info)
        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')


@router.post('/save_file', tags=['transactions'])
async def save_file(token: Token):
    try:
        username, user_type = unpack_token(token.access_token)
        if user_type == "business":
            PAGE_SIZE = 15
            offset = 0
            workbook = Workbook()
            sheet = workbook.active
            headers = ['transaction_id', 'full_name', 'transaction_date', 'ipu', 'prev_number', 'new_number', 'verdict']
            sheet.append(headers)

            while True:
                data = await SQLDatabase.get_transactions_logs(username, offset)
                for dictionary in data:
                    dictionary['transaction_date'] = str(dictionary['transaction_date'])
                if not data:
                    break
                for row in data:
                    row_data = [row[col] for col in headers]
                    sheet.append(row_data)
                offset += PAGE_SIZE

            file_path = 'data.xlsx'
            workbook.save(file_path)
            return FileResponse(file_path, filename='data.xlsx')

        else:
            raise HTTPException(status_code=400, detail="bad user_type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token expired')
    except BadTokenError:
        raise HTTPException(status_code=401, detail='bad token')
