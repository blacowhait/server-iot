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
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    hashed_password = Column(String)
    email = Column(String)
    is_admin = Column(Boolean, default=False)
    activated = Column(Boolean, default=False)
    token = Column(String)
    # image = Column(String, default="example.svg")
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime( 
        timezone=True), default=func.now(), onupdate=func.current_timestamp())
    
class Hardware_DB(Base):
    __tablename__ = 'hardware'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    description = Column(String)

class Node_DB(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    field_sensor = Column(ARRAY(String))
    id_hardware_node = Column(Integer, ForeignKey("hardware.id"))
    id_user = Column(Integer, ForeignKey("account.id"))
    id_hardware_sensor = Column(ARRAY(Integer, ForeignKey("hardware.id")))

class Feed_DB(Base):
    __tablename__ = 'feed'
    id = Column(Integer, primary_key=True, index=True)
    value = Column(ARRAY(Float))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    id_node = Column(Integer, ForeignKey("node.id"))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)