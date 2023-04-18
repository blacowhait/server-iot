from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.db import Hardware_DB
from database.conn_pool import database_instance

# ------------------------ Schema

class HardwareBase(BaseModel):
    id: str
    name: str
    type: str
    description: str

# ------------------------ Class

class Hardware():
    id: str
    name: str
    type: str
    description: str

    # class Config:
    #     orm_mode = True

    def create(uname: str, typ: str, desc: str, db: Session):
        hard = Hardware_DB(
            name = uname,
            type = typ,
            description = desc
        )
        db.add(hard)
        db.commit()
        db.refresh(hard)
        db.close()
        return True
    
    def get_all(db: Session):
        items = db.query(Hardware_DB).all()
        db.close()
        return items
    
    async def check(id: int):
        res = await database_instance.execute(query=f"select type from hardware where id='{id}' and type='sensor';")
        if res == 'SELECT 1':
            return True
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Make sure the hardware has sensor type !")
    
    def get(id: int, db: Session):
        item = db.query(Hardware_DB).filter(Hardware_DB.id == id).first()
        return item

    def update(id: int, nem: str, desc: str, typ: str, db: Session):
        item = db.query(Hardware_DB).filter(Hardware_DB.id == id).first()
        item.description = desc
        item.type = typ
        item.name = nem
        db.commit()
        db.refresh(item)
        db.close()
        return True
    
    def delete(id: int, db: Session):
        item = db.query(Hardware_DB).filter(Hardware_DB.id == id).delete()
        db.commit()
        db.close()
        return True