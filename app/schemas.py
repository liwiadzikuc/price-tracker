from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password:str

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: str
    password: str

class VerifyCode(BaseModel):
    email: str
    code: str

class ProductBase(BaseModel):
    name: str
    url: str
    target_price: float

class ProductCreate(ProductBase):
    user_id: int

class ProductRead(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    target_price: Optional[float] = None