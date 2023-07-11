from fastapi import HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import ARRAY
from sqlalchemy.orm import Session
from database.db import Node_DB
from database.conn_pool import database_instance
from fastapi.concurrency import run_in_threadpool
import asyncio
import concurrent.futures
database_instance = database_instance()

# ------------------------ Schema

class NodeBase(BaseModel):
    id: str
    name: str
    location: str
    id_user: int

# ------------------------ Class

async def func_db(query: str):
    conn = await database_instance.get_con()
    while(1):
        if not conn:
            conn = await database_instance.get_con()
        else:
            break
    try:
        res = await conn.execute(query)
        print("Success", res)
    except:
        print("id node not found")
    await database_instance.release_con(conn)

def executor_db(loop, query: str):
    try :
        return loop.run_until_complete(func_db(query))
    except :
        # all good if this program sent 'Results INSERT 0 1'
        pass

async def waiter(id: int, nme: str, loc: str, idn: int):
    check_node = await database_instance.execute(query=f"select type from hardware where id_hardware='{idn}' and type!='sensor';")
    res = check_node
    if res != 'SELECT 1':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Make sure the hardware has node type ! (single-board computer or microcontroller unit)")
    res = await database_instance.execute(query=f"update node set name='{nme}', location='{loc}', id_hardware={idn} where id_node ='{id}'")
    if res == "UPDATE 1":
        return True
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Something went wrong when update node : {res}")

class Node():
    id: str
    name: str
    location: str
    id_user: int

    # class Config:
    #     orm_mode = True

    async def create(nme: str, loc: str, idn: int, idu: int):
        res = await database_instance.execute(query=f"insert into node (name, location, id_hardware, id_user) values ('{nme}', '{loc}', {idn}, '{idu}')")
        if res == "INSERT 0 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when create node : {res}")
        
    async def update(id: int, nme: str, loc: str, idn: int):
        loop = asyncio.get_running_loop()
        pool = concurrent.futures.ThreadPoolExecutor()
        # res = await loop.run_in_threadpool(executor_db(loop, query=f"update node set name='{nme}', location='{loc}', id_hardware={idn} where id_node ='{id}'"))
        # background_task.add_task(waiter, id, nme, loc, idn)
        try:
            res = await loop.run_in_executor(pool, executor_db(loop, query=f"update node set name='{nme}', location='{loc}', id_hardware={idn} where id_node ='{id}'"))
        except:
            pass
        return True
        
    async def check(id: int, idu: int):
        # pool = concurrent.futures.ProcessPoolExecutor()
        # res = await loop.run_in_executor(pool, database_instance.fetch_rows(query=f"select id_user from node where id_node='{id}';"))
        res = await database_instance.fetch_rows(query=f"select id_user from node where id_node='{id}';")
        if res:
            return True
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You only can access your own node!")

    async def get_field_data(id: int):
        res = await database_instance.fetch_rows(query=f"select field_sensor from node where id_node='{id}';")
        return res

    async def get_all(idu: int):
        res = await database_instance.fetch_rows(query=f"select * from node where id_user='{idu}';")
        return res
    
    async def get(id: int, idu: int):
        res = await database_instance.fetch_rows(query=f"select * from node where id_user='{idu}' and id_node='{id}';")
        return res
    
    def delete(id: int, idu: int, db: Session):
        res = db.query(Node_DB).filter(Node_DB.id_user == idu, Node_DB.id_node == id).delete()
        db.commit()
        db.close()
        print(res)
        if res == 1:
            return True
        else:
            return False