from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import ARRAY
from sqlalchemy.orm import Session
from database.db import Node_DB
from database.conn_pool import database_instance

database_instance = database_instance()

# ------------------------ Schema

class NodeBase(BaseModel):
    id: str
    name: str
    location: str
    id_user: int

# ------------------------ Class

class Node():
    id: str
    name: str
    location: str
    id_user: int

    # class Config:
    #     orm_mode = True

    async def create(nme: str, loc: str, fie: ARRAY(int), idn: int, ids: ARRAY(int), idu: int):
        res = await database_instance.execute(query=f"insert into node (name, location, field_sensor, id_hardware_node, id_hardware_sensor, id_user) values ('{nme}', '{loc}', ARRAY {fie}, {idn}, ARRAY {ids}, '{idu}')")
        if res == "INSERT 0 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when create node : {res}")
        
    async def update(id: int, nme: str, loc: str, fie: ARRAY(int), idn: int, ids: ARRAY(int)):
        print(fie)
        res = await database_instance.execute(query=f"update node set name='{nme}', location='{loc}', field_sensor=ARRAY {fie}, id_hardware_node={idn}, id_hardware_sensor=ARRAY {ids} where id ='{id}'")
        if res == "UPDATE 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when update node : {res}")
        
    async def get_field_data(id: int):
        res = await database_instance.fetch_rows(query=f"select field_sensor from node where id='{id}';")
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
        res = db.query(Node_DB).filter(Node_DB.id_user == idu, Node_DB.id == id).delete()
        db.commit()
        db.close()
        print(res)
        if res == 1:
            return True
        else:
            return False