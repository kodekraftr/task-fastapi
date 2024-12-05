from pydantic import BaseModel, EmailStr,Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name:str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    username: Optional[str] = None
    email:Optional[EmailStr] = None
    password: str

    class Config:
        populate_by_name = True   

class UserData(BaseModel):
    id:int
    email:EmailStr
    name:str
    role:str
    is_active:bool
    manager_name: Optional[str] = None 

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
    name:str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    username: str | None = None


