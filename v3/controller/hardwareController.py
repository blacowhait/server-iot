from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from controller.authController import cookie_checker
from database.db import get_db
from sqlalchemy.orm import Session
from model.hardware import Hardware
from settings import get_settings

settings = get_settings()
templates = Jinja2Templates(directory="./templates")

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
        return templates.TemplateResponse("hardware.html", {"request": request, "datas": list_hardware})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})
    
@router.post('/')
async def create(request: Request, name: str = Form(),  type: str = Form(),  desc: str = Form(), db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        if akun.is_admin:
            if Hardware.create(name, type, desc, db):
                return RedirectResponse("/hardware", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail="error",
                )
        else:
            return templates.TemplateResponse("auth.html", {"request": request, "message": "You are not an Admin, Please login using admin account"})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})

@router.get('/update/{id}')
async def update_form(request: Request, id: int, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        return templates.TemplateResponse("update_hardware.html", {"request": request, "update_id": id})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})

# @router.put('/{id}')
@router.post('/{id}')
async def update_hardware(request: Request, id: int, name: str = Form(),  type: str = Form(),  desc: str = Form(), db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        if akun.is_admin:
            if Hardware.update(id, name, type, desc, db):
                return RedirectResponse("/hardware", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail="error",
                )
        else:
            return templates.TemplateResponse("auth.html", {"request": request, "message": "You are not an Admin, Please login using admin account"})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})
    
# @router.delete('/{id}')
@router.get('/delete/{id}')
async def delete_hardware(request: Request, id: int, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        if akun.is_admin:
            if Hardware.delete(id, db):
                return RedirectResponse("/hardware", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail="error",
                )
        else:
            return templates.TemplateResponse("auth.html", {"request": request, "message": "You are not an Admin, Please login using admin account"})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})