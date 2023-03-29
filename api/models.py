#тут лежат все модели pydantic для запросов, чтоб не срать в код

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    name: str | None = None 
    surname: str | None = None
    email: str | None = None
    phone: str 
    city: str | None = None 
    country: str | None = None 
    adress: str | None = None 

class AdminCreate(BaseModel):
    username: str
    password: str  

class HostCreate(BaseModel):
    name: str
    identifier: str  

class TransactionCreate(BaseModel):
    user_id: int
    summ: float
    currency_id: int 
    type: str