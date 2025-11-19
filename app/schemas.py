from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    url: str
    target_price: float

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
