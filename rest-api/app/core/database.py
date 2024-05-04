import time
from typing import Any

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError as sqlalchemyOpError
from pymysql.err import OperationalError, MySQLError

from app.config import log
from app.config import settings
from app.models.db_models import Base

engine: Engine
SessionLocal: Any


def connect_db():
    global engine
    global SessionLocal
    try:
        engine = create_engine(
            str(settings.DATABASE_URI),
            pool_pre_ping=True,
        )
    except Exception as e:
        log.error(e)
        log.info(f"s = {str(settings.DATABASE_URI)}")
    Base.metadata.bind = engine
    SessionLocal = sessionmaker(bind=engine)


def update_db():
    global Base
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def init_db():
    connected = False
    while not connected:
        try:
            connect_db()
        except (sqlalchemyOpError, MySQLError, OperationalError):
            log.info("failed to connect to db")
            time.sleep(2)
        else:
            connected = True
            # update_db()  # uncomment this line to update db
            log.info("initialized db")
    return SessionLocal

def get_session():
    global SessionLocal
    return SessionLocal

