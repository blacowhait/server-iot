from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from controller.authController import get_current_user
from model.account import Account
from database.db import get_db
from sqlalchemy.orm import Session
from model.node import Node
from model.hardware import Hardware
from settings import get_settings
from pydantic import BaseModel

settings = get_settings()

router = APIRouter(
    prefix="/node",
    tags=['node']
)

class form_add_nd(BaseModel):
    name: str
    location: str
    field_sensor: str
    id_hardware_node: str
    id_hardware_sensor: str

@router.get('/')
async def get_all_Node(db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        list_Node = Node.get_all(akun.id,db)
        return {"List Node":list_Node}
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.get('/{id}')
async def get_all_Node(id: int, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        list_Node = Node.get(id, akun.id, db)
        return {"Detail Node":list_Node}
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
  
@router.post('/')
async def create(form_data: form_add_nd, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    id_hardware_sensor = [int(_) for _ in form_data.id_hardware_sensor.split(',')]
    field_sensor = [_ for _ in form_data.field_sensor.split(',')]
    if not len(id_hardware_sensor) == len(field_sensor):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="len of array must same!",
        )
    if akun:
        for i in id_hardware_sensor:
            if await Hardware.check(i):
                continue
            else:
                return JSONResponse({"message":f"This hardware type is not sensor! id = {i}"}, status_code=400)
        if await Node.create(form_data.name, form_data.location, field_sensor, form_data.id_hardware_node, id_hardware_sensor, akun.id):
            return JSONResponse({"message":"Success add new node!"}, status_code=201)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.put('/{id}')
async def update_Node(id: int, form_data: form_add_nd, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    id_hardware_sensor = [int(_) for _ in form_data.id_hardware_sensor.split(',')]
    field_sensor = [_ for _ in form_data.field_sensor.split(',')]
    if akun:
        for i in id_hardware_sensor:
            if await Hardware.check(i):
                continue
            else:
                return JSONResponse({"message":f"This hardware type is not sensor! id = {i}"}, status_code=400)
        if await Node.update(id, form_data.name, form_data.location, field_sensor, form_data.id_hardware_node, id_hardware_sensor):
            return JSONResponse({"message":f"Success update node, id = {id}!"}, status_code=201)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.delete('/delete/{id}')
async def delete_Node(id: int, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        if Node.delete(id, akun.id, db):
            return JSONResponse({"message":f"Success delete node, id = {id}!"}, status_code=201)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)