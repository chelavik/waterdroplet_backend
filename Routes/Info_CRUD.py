from fastapi import APIRouter
from Models.Models import CheckToken
from Utils.Hasher import HasherClass
from Database.Databases import DatabaseClass


database = DatabaseClass()
HasherObject = HasherClass()
router = APIRouter()

# ---------------------ABOUT US-----------------------------

#get

#put
@router.put('/edit-about-us')
async def edit_about_us(token: CheckToken):
    pass

#-----------------articles(for developers)----------------

#crud
#get all
#get by id

#----------------services---------------

#crud
#get all
