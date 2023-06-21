from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from controller import authController, hardwareController, nodeController, feedController
from controller.authController import get_current_user
from model.account import Account
from database.db import engine
from database.conn_pool import database_instance
from database.db import get_db
from sqlalchemy.orm import Session
from settings import get_settings
from json import dumps

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

settings = get_settings()
database_instance = database_instance()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    # openapi_url=""
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )
app.middleware("http")

app.include_router(authController.router)
app.include_router(hardwareController.router)
app.include_router(nodeController.router)
app.include_router(feedController.router)

@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    # Change here to LOGGER
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})

@cache()
async def get_cache():
    return 1

@app.on_event("startup")
async def startup():
    await database_instance.connect()
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    # app.state.db = database_instance

@app.get('/')
async def index(request: Request, db: Session = Depends(get_db), akun : Account = Depends(get_current_user)):
    try:
        return JSONResponse({"message":f"Hallo {akun.username}"}, status_code=200)
    except:
        return JSONResponse({"message":"Login First!"}, status_code=401)