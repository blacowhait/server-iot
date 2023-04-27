from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from model.account import Account
from database.db import get_db
from sqlalchemy.orm import Session
from settings import get_settings
from datetime import datetime, timedelta
from controller.emailController import send_verification_email, send_forgot_password_email
import jwt
import os
import binascii
from pydantic import BaseModel
templates = Jinja2Templates(directory="./templates")

settings = get_settings()
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

class TokenData(BaseModel):
    email: str | None = None
    is_admin: bool | None = None
    id: int | None = None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET"), algorithm=settings.ALGORITHM)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def cookie_checker(token : str, db: Session):
    auth = jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
    if datetime.fromtimestamp(auth.get("exp")) < datetime.now():
        raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    eml: str = auth.get("sub")
    is_admin: bool = auth.get("is_admin")
    id: int = auth.get("id")
    token_data = TokenData(email=eml, is_admin=is_admin, id=id)
    return token_data # || 1 = 1

@router.get("/activation/")
async def verif_email(email: str, token: str, response: Response, db: Session = Depends(get_db)):
    if Account.check_token(email, token, db):
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) 
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key='user', value=access_token)
        return response
    else:
        raise HTTPException(status_code=400, detail="Invalid token")

@router.post("/regist")
async def regis(request: Request, username: str = Form(), password: str = Form(), email: str = Form(), db : Session = Depends(get_db)):
    token = binascii.b2a_hex(os.urandom(16))
    token = token.decode()
    if Account.is_exist(email, db):
        return templates.TemplateResponse("auth.html", {"request": request, "message":"email is registered"})
    if Account.create(username, email, password, token, db):
        await send_verification_email(email, token)
        # redirect_url = CustomURLProcessor().url_for(request, 'get_card').include_query_params(msg="Succesfully created!")
        return templates.TemplateResponse("auth.html", {"request": request, "message":"verified your email!"})

@router.post("/forgot-password")
async def forgot(request: Request, email: str = Form(), db: Session = Depends(get_db)):
    new_pass = binascii.b2a_hex(os.urandom(16))
    new_pass = new_pass.decode()
    if not Account.is_exist(email, db):
        return templates.TemplateResponse("auth.html", {"request": request, "message":"email not found!"})
    if Account.update(email, new_pass, db):
        await send_forgot_password_email(email, new_pass)
        return templates.TemplateResponse("auth.html", {"request": request, "message":"check your email!"})

@router.post("/login")
async def login(response: Response, password: str = Form(), email: str = Form(), db : Session = Depends(get_db)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)  
    if not Account.is_exist(email, db):
        raise HTTPException(status_code=400, detail="Inactive user")
           
    if Account.check_pass(email, password, db):
        akun = Account.get_user(email, db)
        access_token = create_access_token(
            data={"sub": akun.email, "id": akun.id, "is_admin": akun.is_admin}, expires_delta=access_token_expires
        )
        response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key='user', value=access_token)
        return response
    else:
        print('error')

@router.post("/change-password")
async def change(request: Request, old_password: str = Form(), new_password: str = Form(), db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    acc = await cookie_checker(kue, db)
    if acc:
        change = Account.update_byself(acc.email, old_password, new_password, db)
        if change:
            return templates.TemplateResponse("auth.html", {"request": request, "message":"succesfull change your password!"})
        else:
            return templates.TemplateResponse("auth.html", {"request": request, "message":"wrong old pass!"})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})
    
@router.get("/user")
async def get_user(request: Request, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    acc = await cookie_checker(kue, db)
    if acc:
        return templates.TemplateResponse("user.html", {"request": request, "akun":acc})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})
    
@router.get("/all-user")
async def get_all_user(request: Request, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    acc = await cookie_checker(kue, db)
    if acc.is_admin:
        all_acc = Account.get_all_user(db)
        return templates.TemplateResponse("all_user.html", {"request": request, "akuns":all_acc})
    else:
        return templates.TemplateResponse("auth.html", {"request": request})