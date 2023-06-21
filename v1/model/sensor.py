from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import ARRAY
from sqlalchemy.orm import Session
from database.db import Sensor_DB
from database.db import Node_DB
from database.conn_pool import database_instance

database_instance = database_instance()

# ------------------------ Schema

class SensorBase(BaseModel):
    id_sensor: str
    name: str
    unit: str
    id_node: int
    id_hardware_sensor: int

# ------------------------ Class

class Sensor():
    id_sensor: str
    name: str
    unit: str
    id_node: int
    id_hardware_sensor: int

    # class Config:
    #     orm_mode = True

    async def create(nme: str, unt: str, idn: int, ids: int):
        res = await database_instance.execute(query=f"insert into sensor (name, unit, id_hardware, id_node) values ('{nme}', '{unt}', {ids}, '{idn}')")
        if res == "INSERT 0 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when create sensor : {res}")
        
    async def update(id: int, nme: str, unt: str, idn: int, ids: int):
        res = await database_instance.execute(query=f"update sensor set name='{nme}', unit='{unt}', id_node={idn}, id_hardware={ids} where id_sensor ='{id}'")
        if res == "UPDATE 1":
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Something went wrong when update node : {res}")
        
    async def get_all_rly():
        res = await database_instance.fetch_rows(query=f"select * from sensor;")
        return res
    
    def get_all(idn: int, db: Session):
        nodes = db.query(Sensor_DB).filter(Sensor_DB.id_node == idn).all()
        return nodes
    
    async def get(id: int):
        # res = await database_instance.fetch_rows(query=f"select * from sensor where id_sensor='{id}' and id_user='{idn}';")
        res = await database_instance.fetch_rows(query=f"select * from sensor where id_sensor='{id};")
        return res
    
    def check(id: int, idu: int, db: Session):
        try:
            sensor = db.query(Sensor_DB).filter(Sensor_DB.id_sensor == id).first()
            idn = sensor.id_node
            node = db.query(Node_DB).filter(Node_DB.id_sensor == idn).first()
            niu = node.id_user
        except:
            niu = -1
        if niu == idu:
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"you only can access your own node !")

    def delete(id: int, db: Session):
        res = db.query(Sensor_DB).filter(Sensor_DB.id_sensor == id).delete()
        db.commit()
        db.close()
        print(res)
        if res == 1:
            return True
        else:
            return False