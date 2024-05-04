from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict
from decimal import Decimal


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str | None = None
    surname: str | None = None
    email: EmailStr | None = None
    phone: str
    city: str | None = None
    country: str | None = None
    adress: str | None = None
    avatar_id: int | None = None
    usergroup_id: int | None = None

class Admin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    rights_group_id: int
