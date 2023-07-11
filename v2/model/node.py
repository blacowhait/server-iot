from fastapi import HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import ARRAY
from sqlalchemy.orm import Session
from database.db import Node_DB
from database.conn_pool import database_instance
import asyncio
import concurrent.futures
from fastapi.concurrency import run_in_threadpool

database_instance = database_instance()

# ------------------------ Schema

class NodeBase(BaseModel):
    id: str
    name: str
    location: str
    id_user: int

# ------------------------ Class

async def func_db(idn: int, ids: int, query: str):
    ids = ids.replace('{','').replace('}','')
    id_hardware_sensor = [int(_) for _ in ids.split(',')]
    # valid = True
    # try move the logic to conn pool
    await database_instance.node_trans(idn, id_hardware_sensor, query)

    # # im tried 1 conn pool for full 1 transaction
    # conn = await database_instance.get_con()
    # while(1):
    #     if not conn:
    #         conn = await database_instance.get_con()
    #     else:
    #         break
    # check_node = await conn.execute(query=f"select type from \"hardware\" where id_hardware='{idn}' and type!='sensor';")
    
    # # check_node = await database_instance.execute(query=f"select type from \"hardware\" where id_hardware='{idn}' and type!='sensor';")
    # if check_node == 'SELECT 1':
    #     for i in id_hardware_sensor:
    #         res = await conn.execute(query=f"select type from \"hardware\" where id_hardware='{i}' and type='sensor';")
    #         # res = await database_instance.execute(query=f"select type from \"hardware\" where id_hardware='{i}' and type='sensor';")
    #         if res != 'SELECT 1':
    #             print('not sensor type')
    #             valid = False
    #             break
    # else:
    #     valid = False
    # if valid:
    #     res = await conn.execute(query)
    #     # res = await database_instance.execute(query)
    #     print('Success',res)
    # await database_instance.release_con(conn)

def executor_db(loop, idn: int, ids: int, query: str):
    try:
        # return loop.run_until_complete(database_instance.execute(query))
        return loop.run_until_complete(func_db(idn, ids, query))
    except:
        # all good if this program sent 'Results UPDATE 0 1'
        pass

async def waiter(id: int, nme: str, loc: str, fie: int, idn: int, ids: int):
    # res = await database_instance.execute(query=f"update node set name='{nme}', location='{loc}', field_sensor=ARRAY {fie}, id_hardware_node={idn}, id_hardware_sensor=ARRAY {ids} where id_node ='{id}'")
    res = await database_instance.execute(query=f"update node set name='{nme}', location='{loc}', field_sensor='{fie}', id_hardware_node='{idn}', id_hardware_sensor='{ids}' where id_node ='{id}'")
    if res == "UPDATE 1":
        return True
    else:
        print("error bro",res)
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        # detail=f"Something went wrong when update node : {res}")

class Node():
    id: str
    name: str
    location: str
    id_user: int

    # class Config:
    #     orm_mode = True

    # async def create(nme: str, loc: str, fie: ARRAY(int), idn: int, ids: ARRAY(int), idu: int):
    async def create(nme: str, loc: str, fie: int, idn: int, ids: int, idu: int):
        # res = await database_instance.execute(query=f"insert into node (name, location, field_sensor, id_hardware_node, id_hardware_sensor, id_user) values ('{nme}', '{loc}', ARRAY {fie}, {idn}, ARRAY {ids}, '{idu}')")
        fie = '{'+fie+'}'
        ids = '{'+ids+'}'
        print(nme, loc, fie, idn, ids, idu)
        res = await database_instance.execute(query=f"insert into node (name, location, field_sensor, id_hardware_node, id_hardware_sensor, id_user) values ('{nme}', '{loc}', '{fie}', {idn}, '{ids}', '{idu}')")
        if res == "INSERT 0 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when create node : {res}")
        
    async def update(id: int, nme: str, loc: str, fie: int, idn: int, ids:int):
        fie = '{'+fie+'}'
        ids = '{'+ids+'}'
        loop = asyncio.get_running_loop()
        pool = concurrent.futures.ThreadPoolExecutor()
        # res = await run_in_threadpool(executor_db(loop, query=f"update node set name='{nme}', location='{loc}', field_sensor=ARRAY {fie}, id_hardware_node={idn}, id_hardware_sensor=ARRAY {ids} where id_node ='{id}'"))
        # background_task.add_task(waiter, id, nme, loc, fie, idn, ids)
        try:
            res = await loop.run_in_executor(pool, executor_db(loop, idn, ids, query=f"update node set name='{nme}', location='{loc}', field_sensor='{fie}', id_hardware_node='{idn}', id_hardware_sensor='{ids}' where id_node ='{id}';"))
        except:
            # trust me
            pass
        return True
        
    async def get_field_data(id: int):
        res = await database_instance.fetch_rows(query=f"select field_sensor from node where id_node='{id}';")
        return res

    async def get_all():
        # nodes = db.query(Node_DB).filter(Node_DB.id_user == idu).all()
        nodes = await database_instance.fetch_rows(query=f"select * from node;")
        return nodes
    
    async def get(id: int):
        # node = db.query(Node_DB).filter(Node_DB.id_user == idu, Node_DB.id == id).first()
        node = await database_instance.fetch_rows(query=f"select * from node where id_node='{id}';")
        return node
    
    def delete(id: int, idu: int, db: Session):
        res = db.query(Node_DB).filter(Node_DB.id_user == idu, Node_DB.id_node == id).delete()
        db.commit()
        db.close()
        print(res)
        if res == 1:
            return True
        else:
            return False