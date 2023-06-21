from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from controller.authController import get_current_user
from database.db import get_db
from model.account import Account
from sqlalchemy.orm import Session
from model.channel import Channel
from model.sensor import Sensor
from settings import get_settings
from pydantic import BaseModel

settings = get_settings()

router = APIRouter(
    prefix="/channel",
    tags=['channel']
)

class form_add_channel(BaseModel):
    value: str
    id_sensor: str

@router.post('/')
async def create(form_data: form_add_channel, akun : Account = Depends(get_current_user)):
    if akun:
        if await Channel.create(form_data.id_sensor, form_data.value):
            return JSONResponse({"message":"Success add new channel!"}, status_code=201)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)