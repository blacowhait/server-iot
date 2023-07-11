from fastapi import HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import ARRAY
from sqlalchemy.orm import Session
from database.db import Channel_DB
from database.conn_pool import database_instance
from fastapi.concurrency import run_in_threadpool
import asyncio
import concurrent.futures

database_instance = database_instance()

# ------------------------ Schema

class ChannelBase(BaseModel):
    id_channel: int
    id_sensor: int
    value: float

# ------------------------ Class

async def func_db(ids: int, query: str):
    conn = await database_instance.get_con()
    while(1):
        if not conn:
            conn = await database_instance.get_con()
        else:
            break
    res = await conn.fetch(query=f"select * from sensor where id_sensor='{ids}';")
    if not res:
        print('id sensor not found')
    else:
        res = await conn.execute(query)
        print("Success", res)
    await database_instance.release_con(conn)
    
def executor_db(loop, ids: int, query: str):
    try :
        return loop.run_until_complete(func_db(ids, query))
    except :
        # all good if this program sent 'Results INSERT 0 1'
        pass

async def waiter(ids: int, val: float):
    res = await database_instance.execute(query=f"insert into channel (value, id_sensor) values ('{val}', '{ids}');")
    if res == "INSERT 0 1":
        return True
    else:
        print(res)

class Channel():
    id_channel: int
    id_sensor: int
    value: float

    # class Config:
    #     orm_mode = True

    # async def create(background_task: BackgroundTasks, ids: int, val:float):
    async def create(ids: int, val:float):
        loop = asyncio.get_running_loop()
        pool = concurrent.futures.ThreadPoolExecutor()
        # res = await loop.run_in_threadpool(executor_db(loop, query=f"insert into channel (value, id_sensor) values ('{val}', '{ids}');"))
        # background_task.add_task(waiter, ids, val)
        try : 
            res = await loop.run_in_executor(pool, executor_db(loop, ids, query=f"insert into channel (value, id_sensor) values ('{val}', '{ids}');"))
        except:
            # trust me
            pass
        return True