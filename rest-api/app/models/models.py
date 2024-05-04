from pydantic import BaseModel, EmailStr


class UserInDB(BaseModel):
    """
    User in database schema
    """
    id: int
    username: str
    name: str | None = None
    surname: str | None = None
    email: EmailStr | None = None
    password_hash: str
    phone: str
    avatar_id: int
    usergroup_id: int
    city: str | None = None
    country: str | None = None
    adress: str | None = None

class AdminInDB(BaseModel):
    """
    Admin in database schema
    """
    id: int
    username: str
    rights_group_id: int
    password_hash: str