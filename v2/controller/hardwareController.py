from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from controller.authController import cookie_checker
from database.db import get_db
from sqlalchemy.orm import Session
from model.hardware import Hardware
from settings import get_settings

settings = get_settings()

router = APIRouter(
    prefix="/hardware",
    tags=['hardware']
)

@router.get('/')
async def get_all_hardware(request: Request, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        list_hardware = Hardware.get_all(db)
        return JSONResponse({"datas": list_hardware}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.post('/add')
async def create(request: Request, name: str = Form(),  type: str = Form(),  desc: str = Form(), db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        if Hardware.create(name, type, desc, db):
            return RedirectResponse("/hardware", status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.get('/update/{id}')
async def update_form(request: Request, id: int, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        return JSONResponse({"message":"Just Add"}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

# @router.put('/add/{id}')
@router.post('/add/{id}')
async def update_hardware(request: Request, id: int, name: str = Form(),  type: str = Form(),  desc: str = Form(), db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        if Hardware.update(id, name, type, desc, db):
            return RedirectResponse("/hardware", status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
# @router.delete('/delete/{id}')
@router.get('/delete/{id}')
async def delete_hardware(request: Request, id: int, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        if Hardware.delete(id, db):
            return RedirectResponse("/hardware", status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)