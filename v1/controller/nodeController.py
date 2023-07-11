from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from controller.authController import get_current_user
from database.db import get_db
from sqlalchemy.orm import Session
from model.account import Account
from model.node import Node
from model.hardware import Hardware
from settings import get_settings
from pydantic import BaseModel
from fastapi_cache.decorator import cache

@cache()
async def get_cache():
    return 1

settings = get_settings()

router = APIRouter(
    prefix="/node",
    tags=['node']
)

class form_add_nd(BaseModel):
    name: str
    location: str
    id_hardware: str

async def add_to_db(id, form_data):
    try:
        if await Node.update(id, form_data.name, form_data.location, form_data.id_hardware):
            print('Success')
    except Exception as e:
        print(e)

@router.get('/')
@cache(expire=3000)
async def get_all_Node(akun : Account = Depends(get_current_user)):
    if akun:
        list_Node = await Node.get_all(akun.id_user)
        return JSONResponse({"List Node":list_Node}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.get('/{id}')
@cache(expire=3000)
async def get_all_Node(id: int, akun : Account = Depends(get_current_user)):
    if akun:
        list_Node = await Node.get(id, akun.id_user)
        return JSONResponse({"Detail Node":list_Node}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
  
@router.post('/')
async def create(form_data: form_add_nd, akun : Account = Depends(get_current_user)):
    if akun:
        try:
            int(form_data.id_hardware)
        except:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="Id hardware must integer",
            )

        await Hardware.check_node(form_data.id_hardware)
        if await Node.create(form_data.name, form_data.location, form_data.id_hardware, akun.id_user):
            return JSONResponse({"message":"Success add new node!"}, status_code=201)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.put('/{id}')
async def update_Node(id: int, form_data: form_add_nd, akun : Account = Depends(get_current_user)):
    if akun:
        try:
            int(form_data.id_hardware)
        except:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="Id hardware must integer",
            )

        await add_to_db(id, form_data)
        return JSONResponse({"message":f"Success update node, id = {id}!"}, status_code=201)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.delete('/{id}')
async def delete_Node(id: int, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        if Node.delete(id, akun.id_user, db):
            return JSONResponse({"message":f"Success delete node, id = {id}!"}, status_code=201)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)