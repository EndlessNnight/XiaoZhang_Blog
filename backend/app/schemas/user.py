from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str
    is_admin: bool = False

class UserCreate(UserBase):
    password: str
    verificationCode: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    avatar: Optional[str] = None
    verificationCode: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True 