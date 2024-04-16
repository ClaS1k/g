from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import text

from datetime import datetime

from typing import Union

from app.models import db_models, models
from app.schemas import response_schemas, request_schemas
from app.config import log
from app.utils.token import get_password_hash
import os

def get_user(db: Session, username: Union[str, None]) -> Union[models.UserInDB, None]:
    try:
        user = (
            db.query(db_models.User)
            .filter(
                db_models.User.username == username,
            )
            .one()
        )
        user = models.UserInDB(
            id=user.user_id,
            username=user.username,
            name=user.name,
            surname=user.surname,
            email=user.email,
            password_hash=user.password_hash,
            phone=user.phone,
            city=user.city,
            country=user.country,
            adress=user.address,
            avatar_id=user.avatar_id,
            usergroup_id=user.usergroup_id,
        )
        return user
    except NoResultFound:
        return None

def get_admin(db: Session, username: Union[str, None]) -> Union[models.AdminInDB, None]:
    try:
        admin = (
            db.query(db_models.Admin)
            .filter(
                db_models.Admin.username == username,
            )
            .one()
        )
        admin = models.AdminInDB(
            id=admin.id,
            username=admin.username,
            rights_group_id=admin.rights_group_id,
            password_hash=admin.password_hash,
        )
        return admin
    except NoResultFound:
        return None

def raw_query(db: Session, query: str) -> Union[dict, None]:
    if "SELECT" not in query:
        db.execute(text(query))
        db.commit()
        return None
    else:
        try:
            result = db.execute(text(query)).mappings().all()
            if result is None:
                return []
            else:
                # convert list of dicts to list of lists
                result = [list(row.values()) for row in result]
                log.debug(f"result: {result}")
                return result
        except Exception as ex:
            log.exception(f"failed to execute query {ex}")
            return None
