from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import ARRAY
from sqlalchemy.orm import Session
from database.db import Channel_DB
from database.conn_pool import database_instance

database_instance = database_instance()

# ------------------------ Schema

class ChannelBase(BaseModel):
    id_channel: int
    id_sensor: int
    value: float

# ------------------------ Class

class Channel():
    id_channel: int
    id_sensor: int
    value: float

    # class Config:
    #     orm_mode = True

    async def create(ids: int, val:float):
        res = await database_instance.execute(query=f"insert into channel (value, id_sensor) values ('{val}', '{ids}');")
        if res == "INSERT 0 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when create channel : {res}")