from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from controller.authController import cookie_checker
from database.db import get_db
from sqlalchemy.orm import Session
from model.node import Node
from settings import get_settings

settings = get_settings()
templates = Jinja2Templates(directory="./templates")

router = APIRouter(
    prefix="/node",
    tags=['node']
)

@router.get('/')
async def get_all_Node(request: Request, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        list_Node = Node.get_all(akun.id,db)
        return templates.TemplateResponse("node.html", {"request": request, "datas": list_Node})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})
    
@router.post('/')
async def create(request: Request, name: str = Form(),  location: str = Form(), field_sensor: str = Form(), id_hardware_node: str = Form(), id_hardware_sensor: str = Form(), db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    id_hardware_sensor = [int(_) for _ in id_hardware_sensor.split(',')]
    field_sensor = [_ for _ in field_sensor.split(',')]
    if not len(id_hardware_sensor) == len(field_sensor):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="len of array must same!",
        )
    if akun:
        if await Node.create(name, location, field_sensor, id_hardware_node, id_hardware_sensor, akun.id):
            return RedirectResponse("/node", status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return templates.TemplateResponse("auth.html", {"request": request})

@router.get('/update/{id}')
async def update_form(request: Request, id: int, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        return templates.TemplateResponse("update_node.html", {"request": request, "update_id": id})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})

# @router.put('/{id}')
@router.post('/{id}')
async def update_Node(request: Request, id: int, name: str = Form(),  location: str = Form(), field_sensor: str = Form(), id_hardware_node: str = Form(), id_hardware_sensor: str = Form(), db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    id_hardware_sensor = [int(_) for _ in id_hardware_sensor.split(',')]
    field_sensor = [_ for _ in field_sensor.split(',')]
    if akun:
        if await Node.update(id, name, location, field_sensor, id_hardware_node, id_hardware_sensor):
            return RedirectResponse("/node", status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return templates.TemplateResponse("auth.html", {"request": request})
    
# @router.delete('/{id}')
@router.get('/delete/{id}')
async def delete_Node(request: Request, id: int, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    akun = await cookie_checker(kue, db)
    if akun:
        if Node.delete(id, akun.id, db):
            return RedirectResponse("/node", status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="error",
            )
    else:
        return templates.TemplateResponse("auth.html", {"request": request})