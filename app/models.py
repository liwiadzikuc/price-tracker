from app.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    target_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float, nullable=False)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")

class PriceAlert(Base):
    __tablename__="price_alerts"
    id=Column(Integer,primary_key=True,index=True)
    product_id=Column(Integer, ForeignKey("products.id"))
    price=Column(Float, nullable=False)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    product=relationship("Product")