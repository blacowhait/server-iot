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
    token = Column(String)
    # image = Column(String, default="example.svg")
    # time_created = Column(DateTime(timezone=True), server_default=func.now())
    # time_updated = Column(DateTime( 
    #     timezone=True), default=func.now(), onupdate=func.current_timestamp())
    
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
    id_hardware = Column(Integer, ForeignKey("hardware.id"))
    id_user = Column(Integer, ForeignKey("user_person.id"))

class Sensor_DB(Base):
    __tablename__ = 'sensor'
    id_sensor = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    unit = Column(String)
    id_node = Column(Integer, ForeignKey("node.id"))
    id_hardware = Column(Integer, ForeignKey("hardware.id"))

class Channel_DB(Base):
    __tablename__ = 'channel'
    id_channel = Column(Integer, primary_key=True, index=True)
    value = Column(Float)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    id_sensor = Column(Integer, ForeignKey("sensor.id"))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)