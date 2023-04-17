from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from model.account import Account
from database.db import get_db
from sqlalchemy.orm import Session
from settings import get_settings
from datetime import datetime, timedelta
from controller.emailController import send_verification_email, send_forgot_password_email
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Annotated
from pydantic import BaseModel
import jwt
import os
import binascii

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
settings = get_settings()
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class form_data(BaseModel):
    email: str
    password: str

class form_data_regist(BaseModel):
    email: str
    password: str
    username: str

class form_data_change(BaseModel):
    old_password: str
    new_password: str

class Email(BaseModel):
    email: str

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

# async def cookie_checker(token : str, db: Session):
#     auth = jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
#     if datetime.fromtimestamp(auth.get("exp")) < datetime.now():
#         raise HTTPException(
#                 status_code = status.HTTP_401_UNAUTHORIZED,
#                 detail="Token expired",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#     eml: str = auth.get("sub")
#     user = Account.get_user(eml, db)
#     return user # || 1 = 1

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db : Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = Account.get_user(token_data.email, db)
    if user is None:
        raise credentials_exception
    return user

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
async def regis(form_data: form_data_regist, db : Session = Depends(get_db)):
    token = binascii.b2a_hex(os.urandom(16))
    token = token.decode()
    if Account.is_exist(form_data.email, db):
        return JSONResponse({"msg":"User Already Exist"}, status_code=400)
    print(form_data)
    if Account.create(form_data.username, form_data.email, form_data.password, token, db):
        await send_verification_email(form_data.email, token)
        return JSONResponse({"msg":"Check Your Email"}, status_code=201)

@router.post("/forgot-password")
async def forgot(email: Email, db: Session = Depends(get_db)):
    new_pass = binascii.b2a_hex(os.urandom(16))
    new_pass = new_pass.decode()
    print(new_pass)
    if not Account.is_exist(email.email, db):
        return JSONResponse({"msg":"Email not found"}, status_code=400)
    if Account.update(email.email, new_pass, db):
        await send_forgot_password_email(email.email, new_pass)
        return JSONResponse({"msg":"Check Your Email"}, status_code=200)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: form_data, db : Session = Depends(get_db)):
    user = Account.check_pass(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: form_data, db : Session = Depends(get_db)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)  
    email = form_data.email
    password = form_data.password
    if not Account.is_exist(email, db):
        raise HTTPException(status_code=400, detail="Inactive user")
           
    if Account.check_pass(email, password, db):
        akun = Account.get_user(email, db)
        access_token = create_access_token(
            data={"sub": akun.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        return JSONResponse({"message":"Incorrect username or password"}, status_code=401)

@router.post("/change-password")
async def change(form_data: form_data_change, db: Session = Depends(get_db), acc: Account = Depends(get_current_user)):
    if acc:
        change = Account.update_byself(acc.email, form_data.old_password, form_data.new_password, db)
        if change:
            return JSONResponse({"message":"succesfull change your password!"}, status_code=200)
        else:
            return JSONResponse({"message":"wrong old pass!"}, status_code=400)
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.get("/user")
async def get_user(acc : Account = Depends(get_current_user)):
    if acc:
        return {"akun":acc}
    else:
        return JSONResponse({"message":"Login First"}, status_code=401)
    
@router.get("/all-user")
async def get_all_user(acc : Account = Depends(get_current_user), db : Session = Depends(get_db)):
    if acc.is_admin:
        all_acc = Account.get_all_user(db)
        return {"List_akun":all_acc}
    else:
        return JSONResponse({"message":"account is not admin"}, status_code=403)