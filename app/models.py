from app.db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    target_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())