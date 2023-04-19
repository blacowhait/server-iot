from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from controller.authController import get_current_user
from model.account import Account
from database.db import get_db
from sqlalchemy.orm import Session
from model.hardware import Hardware
from settings import get_settings
from pydantic import BaseModel

settings = get_settings()

router = APIRouter(
    prefix="/hardware",
    tags=['hardware']
)

class form_add_hw(BaseModel):
    name: str
    type: str
    desc: str

@router.get('/')
async def get_all_hardware(db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        list_hardware = Hardware.get_all(db)
        return {"List Hardware":list_hardware}
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.get('/{id}')
async def get_hardware(id: int, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        hardware = Hardware.get(id, db)
        return {"Detail Hardware": hardware}
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.post('/')
async def create(form_data: form_add_hw, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        if akun.is_admin:
            if Hardware.create(form_data.name, form_data.type, form_data.desc, db):
                return JSONResponse({"message":"Success add new hardware!"}, status_code=201)
            else:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail="error",
                )
        else:
            return JSONResponse({"message":"Only admin can do it!"}, status_code=403)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.put('/{id}')
async def update_hardware(id : int, form_data: form_add_hw, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        if akun.is_admin:
            if Hardware.update(id, form_data.name, form_data.type, form_data.desc, db):
                return JSONResponse({"message":f"Success update hardware with id = {id} !"}, status_code=201)
            else:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail="error",
                )
        else:
            return JSONResponse({"message":"Only admin can do it!"}, status_code=403)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.delete('/delete/{id}')
async def delete_hardware(id : int, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        if akun.is_admin:
            if Hardware.delete(id, db):
                return JSONResponse({"message":f"Success delete hardware with id = {id} !"}, status_code=200)
            else:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail="error",
                )
        else:
            return JSONResponse({"message":"Only admin can do it!"}, status_code=403)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)