from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from model.account import Account
from database.db import get_db
from sqlalchemy.orm import Session
from settings import get_settings
from datetime import datetime, timedelta
from controller.emailController import send_verification_email, send_forgot_password_email
import jwt
import os
import binascii

settings = get_settings()
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

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
    user = Account.get_user(eml, db)
    return user # || 1 = 1

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
        return JSONResponse({"msg":"User Already Exist"}, status_code=400)
    if Account.create(username, email, password, token, db):
        await send_verification_email(email, token)
        return JSONResponse({"msg":"Check Your Email"}, status_code=201)

@router.post("/forgot-password")
async def forgot(request: Request, email: str = Form(), db: Session = Depends(get_db)):
    new_pass = binascii.b2a_hex(os.urandom(16))
    new_pass = new_pass.decode()
    if not Account.is_exist(email, db):
        return JSONResponse({"msg":"Email not found"}, status_code=400)
    if Account.update(email, new_pass, db):
        await send_forgot_password_email(email, new_pass)
        return JSONResponse({"msg":"Check Your Email"}, status_code=200)

@router.post("/login")
async def login(response: Response, password: str = Form(), email: str = Form(), db : Session = Depends(get_db)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)  
    if not Account.is_exist(email, db):
        raise HTTPException(status_code=400, detail="Inactive user")
           
    if Account.check_pass(email, password, db):
        akun = Account.get_user(email, db)
        access_token = create_access_token(
            data={"sub": akun.email}, expires_delta=access_token_expires
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
            return JSONResponse({"message":"succesfull change your password!"}, status_code=200)
        else:
            return JSONResponse({"message":"wrong old pass!"}, status_code=400)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.get("/user")
async def get_user(request: Request, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    acc = await cookie_checker(kue, db)
    if acc:
        return JSONResponse({"akun":acc}, status_code=200)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.get("/all-user")
async def get_all_user(request: Request, db: Session = Depends(get_db)):
    kue = request.cookies.get('user')
    acc = await cookie_checker(kue, db)
    if acc.is_admin:
        all_acc = Account.get_all_user(db)
        return JSONResponse({"akuns":all_acc}, status_code=200)
    else:
        return JSONResponse({"message":"account is not admin"}, status_code=403)