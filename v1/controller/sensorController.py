from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from controller.authController import get_current_user
from database.db import get_db
from model.account import Account
from sqlalchemy.orm import Session
from model.sensor import Sensor
from model.node import Node
from model.hardware import Hardware
from settings import get_settings
from pydantic import BaseModel

settings = get_settings()

router = APIRouter(
    prefix="/sensor",
    tags=['sensor']
)

class form_add_sensor(BaseModel):
    name: str
    unit: str
    id_node: int
    id_hardware_sensor: int

@router.get('/{idn}')
async def get_all_sensor(idn: int, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        if await Node.check(idn, akun.id):
            list_sensor = Sensor.get_all(idn,db)
            return {"List Sensor":list_sensor}
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.get('/{idn}/{id}')
async def get_sensor(idn: int, id: int, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        if await Node.check(idn, akun.id):
            list_sensor = Sensor.get(id, idn, db)
            return {"List sensor":list_sensor}
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.post('/')
async def create(form_data: form_add_sensor, akun : Account = Depends(get_current_user)):
    if akun:
        if await Node.check(form_data.id_node, akun.id):
            if await Hardware.check(form_data.id_hardware_sensor):
                if await Sensor.create(form_data.name, form_data.unit, form_data.id_node, form_data.id_hardware_sensor):
                    return JSONResponse({"message":"Success add new sensor!"}, status_code=201)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.put('/{id}')
async def update(id: int, form_data: form_add_sensor, akun: Account = Depends(get_current_user)):
    if akun:
        if await Node.check(form_data.id_node, akun.id):
            if await Hardware.check(form_data.id_hardware_sensor):
                if await Sensor.update(id, form_data.name, form_data.unit, form_data.id_node, form_data.id_hardware_sensor):
                    return JSONResponse({"message":f"Success update sensor with id = {id}!"}, status_code=201)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.delete('/delete/{id}')
async def delete(id: int, db: Session = Depends(get_db), akun: Account = Depends(get_current_user)):
    if akun:
        if Sensor.check(id, akun.id, db):
            if Sensor.delete(id, db):
                return JSONResponse({"message":f"Success delete sensor with id = {id} !"}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)