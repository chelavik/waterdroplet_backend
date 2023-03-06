from fastapi import APIRouter, HTTPException
from Models.Models import CheckToken
from Utils.Hasher import HasherClass
from Database.Databases import DatabaseClass


database = DatabaseClass()
HasherObject = HasherClass()
router = APIRouter()

# ---------------------ABOUT US-----------------------------

#get
@router.get('/about-us')
async def get_about_us():
    try:
        return await database.get_about_us()
    except:
        raise HTTPException(status_code=500, detail='Database Error')

#put
@router.put('/edit-about-us')
async def edit_about_us(token: CheckToken, text: str):
    pass

#-----------------articles(for developers)----------------

#crud
#get all
#get by id

#----------------services---------------

#crud
#get all
