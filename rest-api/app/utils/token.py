from app.core import crud
from app.config import settings
from app.core.dependencies import pwd_context, oauth2_scheme, get_db
from app.schemas.response_schemas import TokenData, User, Admin
from app.config import log

from jose import jwt, JWTError
from typing import Optional, Annotated
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session


def verify_password(plain_password, hashed_password):
    log.info(f"Verifying password {plain_password} against {hashed_password}")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user(db, username)
    if user is None:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def authenticate_admin(db: Session, username: str, password: str):
    admin = crud.get_admin(db, username)
    if admin is None:
        return False
    if not verify_password(password, admin.password_hash):
        return False
    return admin

no_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None or token == "":
        return None
    log.info(f'Getting current user from token {token}')
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        log.info(f'{payload}')
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc
    user = crud.get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    user = User(
        id=user.id,
        username=user.username,
        name=user.name,
        surname=user.surname,
        email=user.email,
        phone=user.phone,
        city=user.city,
        country=user.country,
        adress=user.adress,
        avatar_id=user.avatar_id,
        usergroup_id=user.usergroup_id,
    )
    return user

def get_current_admin(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None or token == "":
        return None
    log.info(f'Getting current admin from token {token}')
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        log.info(f'{payload}')
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc
    admin = crud.get_admin(db, username=token_data.username)
    if admin is None:
        raise credentials_exception
    admin = Admin(
        id=admin.id,
        username=admin.username,
        rights_group_id=admin.rights_group_id,
    )
    return admin

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user is None:
        raise no_token_exception
    return current_user

async def get_current_soft_client(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

async def get_current_active_admin(
    current_admin: Annotated[Admin, Depends(get_current_admin)]
):
    if current_admin is None:
        raise no_token_exception
    return current_admin

