from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import ARRAY
from sqlalchemy.orm import Session
from database.db import Feed_DB
from database.conn_pool import database_instance

database_instance = database_instance()

# ------------------------ Schema

class FeedBase(BaseModel):
    id: str
    id_node: int

# ------------------------ Class

class Feed():
    id: str
    id_node: int

    # class Config:
    #     orm_mode = True

    async def create(id: int, val: ARRAY(float)):
        res = await database_instance.execute(query=f"insert into feed (value, id_node) values (ARRAY {val}, '{id}');")
        if res == "INSERT 0 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when create feed : {res}")
    
    async def get_len(id: int):
        res = await database_instance.fetch_rows(query=f"select field_sensor from node where id='{id}';")
        return res
    
    async def get_feed_data(id: int):
        res = await database_instance.fetch_rows(query=f"select value,time_created from feed where id_node='{id}' order by id desc limit 7;")
        return res