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

    async def create(nme: str, loc: str, idn: int, idu: int):
        res = await database_instance.execute(query=f"insert into node (name, location, id_hardware_node, id_user) values ('{nme}', '{loc}', {idn}, '{idu}')")
        if res == "INSERT 0 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when create node : {res}")
        
    async def update(id: int, nme: str, loc: str, idn: int):
        res = await database_instance.execute(query=f"update node set name='{nme}', location='{loc}', id_hardware_node={idn} where id ='{id}'")
        if res == "UPDATE 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when update node : {res}")
        
    async def check(id: int, idu: int):
        res = await database_instance.execute(query=f"select id_user from node where id='{id}';")
        if res == "SELECT 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"You only can access your own node!")

    async def get_field_data(id: int):
        res = await database_instance.fetch_rows(query=f"select field_sensor from node where id='{id}';")
        return res

    def get_all(idu: int, db: Session):
        nodes = db.query(Node_DB).filter(Node_DB.id_user == idu).all()
        return nodes
    
    def get(id: int, idu: int, db: Session):
        node = db.query(Node_DB).filter(Node_DB.id_user == idu, Node_DB.id == id).first()
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