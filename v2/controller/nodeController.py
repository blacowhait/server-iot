from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from controller.authController import get_current_user
from model.account import Account
from database.db import get_db
from sqlalchemy.orm import Session
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
    field_sensor: str
    id_hardware_node: str
    id_hardware_sensor: str

async def add_to_db_create(id_user, form_data):
    try:
        id_hardware_sensor = [int(_) for _ in form_data.id_hardware_sensor.split(',')]
    except:
        raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail=f"Id hardware must integer : {form_data.id_hardware_sensor}",
            )
    field_sensor = [_ for _ in form_data.field_sensor.split(',')]
    if not len(id_hardware_sensor) == len(field_sensor):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="len of array must same!",
        )
    for i in id_hardware_sensor:
        try:
            int(i)
        except:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail=f"Id hardware must integer : {i}",
            )
        if await Hardware.check(i):
            pass
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail=f"not sensor hardware type : {i}",
            )
    print(id_user)
    if await Node.create(form_data.name, form_data.location, form_data.field_sensor, form_data.id_hardware_node, form_data.id_hardware_sensor, id_user):
        pass
    else:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="error when insert",
        )

async def add_to_db_update(id, form_data):
    # try:
    id_hardware_sensor = [int(_) for _ in form_data.id_hardware_sensor.split(',')]
    field_sensor = [_ for _ in form_data.field_sensor.split(',')]
    if not len(id_hardware_sensor) == len(field_sensor):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="len of array must same!",
        )
    for i in id_hardware_sensor:
        try:
            int(i)
        except:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail=f"Id hardware must integer : {i}",
            )
    if await Node.update(id, form_data.name, form_data.location, form_data.field_sensor, form_data.id_hardware_node, form_data.id_hardware_sensor):
        pass
    else:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="error when update",
        )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code = status.HTTP_400_BAD_REQUEST,
    #         detail=e,
    #     )

@router.get('/')
@cache(expire=3000)
async def get_all_Node(akun : Account = Depends(get_current_user)):
    if akun:
        list_Node = await Node.get_all()
        # return {"List Node":list_Node}
        return JSONResponse({"List Node":list_Node}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.get('/{id}')
@cache(expire=3000)
async def get_all_Node(id: int, akun : Account = Depends(get_current_user)):
    if akun:
        list_Node = await Node.get(id)
        # return {"Detail Node":list_Node}
        return JSONResponse({"List Node":list_Node}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
  
@router.post('/')
async def create(background_task: BackgroundTasks, form_data: form_add_nd, akun : Account = Depends(get_current_user)):
    if akun:
        await Hardware.check_node(form_data.id_hardware_node)
        await add_to_db_create(akun.id, form_data)
        return JSONResponse({"message":"Success add new node!"}, status_code=201)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)

@router.put('/{id}')
async def update_Node(background_task: BackgroundTasks, id: int, form_data: form_add_nd, akun : Account = Depends(get_current_user)):
    if akun:
        await add_to_db_update(id, form_data)
        return JSONResponse({"message":f"Success update new node! with id : {id}"}, status_code=201)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.delete('/{id}')
async def delete_Node(id: int, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    if akun:
        if Node.delete(id, akun.id, db):
            return JSONResponse({"message":f"Success delete node, id = {id}!"}, status_code=201)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="This is not your node or node not found",
            )
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
