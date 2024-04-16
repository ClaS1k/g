from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from typing import Annotated
from datetime import timedelta

from app.config import log
from app.schemas import response_schemas, request_schemas
from app.core.dependencies import get_db
from app.core import crud
from app.config import settings
from app.utils.token import (
    authenticate_user,
    create_access_token,
    authenticate_admin,
)

router = APIRouter(
    prefix="/user",
    tags=["auth"],
)


@router.post("/token", response_model=response_schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    we use username in OAuth2PasswordRequestForm as email
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # try admin
        admin = authenticate_admin(db, form_data.username, form_data.password)
        if not admin:
            log.error("Incorrect username or password")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            user = admin
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
