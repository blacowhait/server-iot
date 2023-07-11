from fastapi import HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import ARRAY
from sqlalchemy.orm import Session
from database.db import Feed_DB
from database.conn_pool import database_instance
import asyncio
import concurrent.futures

database_instance = database_instance()

# ------------------------ Schema

class FeedBase(BaseModel):
    id: str
    id_node: int

# ------------------------ Class

async def func_db(id:int, val:float, query:str):
    len_val = len(val.split(','))

    # im tried 1 conn pool for full 1 transaction
    conn = await database_instance.get_con()
    while(1):
        if not conn:
            conn = await database_instance.get_con()
        else:
            break
    res = await conn.fetch(query=f"select field_sensor from node where id_node='{id}';")
    res = await database_instance.jsonify(res)

    # res = await database_instance.fetch_rows(query=f"select field_sensor from node where id_node='{id}';")
    try:
        if str(len(res[0]["field_sensor"])) == str(len_val):
            res = await conn.execute(query)
            # res = await database_instance.execute(query)
            print('Succes',res)
        else:
            print('len not same')
    except:
        print('node not found')
    await database_instance.release_con(conn)

def executor_db(loop, id:int, val:float, query:str):
    try:
        # return loop.run_until_complete(database_instance.execute(query))
        return loop.run_until_complete(func_db(id, val, query))
    except:
        # all good if this program sent 'Results INSERT 0 1'
        pass

# async def waiter(id: int, val: ARRAY(float)):
async def waiter(id: int, val: float):
    # res = await database_instance.execute(query=f"insert into feed (time, value, id_node) values (current_timestamp, ARRAY {val}, '{id}');")
    res = await database_instance.execute(query=f"insert into feed (time, value, id_node) values (current_timestamp, '{val}', '{id}');")
    if res == "INSERT 0 1":
        return True
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Something went wrong when create feed : {res}")

class Feed():
    id: str
    id_node: int

    # class Config:
    #     orm_mode = True

    async def create(id: int, val: float):
        val = '{' + val + '}'
        loop = asyncio.get_running_loop()
        pool = concurrent.futures.ThreadPoolExecutor()
        try:
            res = await loop.run_in_executor(pool, executor_db(loop, id, val, query=f"insert into feed (time, value, id_node) values (current_timestamp, '{val}', '{id}');"))
        except:
            # 'trust me'
            pass
        # res = await run_in_threadpool(executor_db(loop, query=f"insert into feed (time, value, id_node) values (current_timestamp, ARRAY {val}, '{id}');"))
        # loop.create_task(waiter(id, val))
        return True
    
    async def get_len(id: int):
        res = await database_instance.fetch_rows(query=f"select count(field_sensor) from node where id_node='{id}';")
        return res
    
    async def get_feed_data(id: int):
        res = await database_instance.fetch_rows(query=f"select value,time from feed where id_node='{id}' order by id_node desc limit 7;")
        return res