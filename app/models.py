from app.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False) 
    products = relationship("Product", back_populates="owner", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    target_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="products")
    history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float, nullable=False)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="history")

class PriceAlert(Base):
    __tablename__="price_alerts"
    id=Column(Integer,primary_key=True,index=True)
    product_id=Column(Integer, ForeignKey("products.id",ondelete="CASCADE")) 
    price=Column(Float, nullable=False)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    product=relationship("Product", back_populates="alerts")