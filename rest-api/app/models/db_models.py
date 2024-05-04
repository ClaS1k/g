from sqlalchemy import (
    Column,
    Integer,
    TEXT,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(TEXT, nullable=False)
    password_hash = Column(TEXT, nullable=False)
    name = Column(TEXT, nullable=False)
    surname = Column(TEXT, nullable=False)
    usergroup_id = Column(Integer, nullable=False)
    avatar_id = Column(Integer, nullable=False)
    email = Column(TEXT, nullable=False)
    phone = Column(TEXT, nullable=False)
    country = Column(TEXT, nullable=False)
    city = Column(TEXT, nullable=False)
    address = Column(TEXT, nullable=False)
    calculation_method = Column(Integer, default=1, nullable=False)

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    username = Column(TEXT, nullable=False)
    password_hash = Column(TEXT, nullable=False)
    rights_group_id = Column(Integer, nullable=False)