from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Boolean, ARRAY, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import get_settings
import os

settings = get_settings()
# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Account_DB(Base):
    __tablename__ = 'user_person'
    id_user = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)
    isadmin = Column(Boolean, default=False)
    status = Column(Boolean, default=False)
    
class Hardware_DB(Base):
    __tablename__ = 'hardware'
    id_hardware = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    description = Column(String)

class Node_DB(Base):
    __tablename__ = 'node'
    id_node = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    # field_sensor = Column(ARRAY(String))
    field_sensor = Column(String[10])
    id_hardware_node = Column(Integer, ForeignKey("user_person.id_user"))
    id_user = Column(Integer, ForeignKey("user_person.id_user"))
    # id_hardware_sensor = Column(ARRAY(Integer))
    id_hardware_sensor = Column(Integer[10])
    is_public = Column(Boolean, default=False)

class Feed_DB(Base):
    __tablename__ = 'feed'
    id = Column(Integer, primary_key=True, index=True)
    # value = Column(ARRAY(Float))
    value = Column(Float[10])
    time = Column(DateTime(timezone=True), server_default=func.now())
    id_node = Column(Integer, ForeignKey("node.id_node"))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)