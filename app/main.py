from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.schemas import ProductCreate, ProductRead
from app.crud import create_product, get_products

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/products", response_model=ProductRead)
def add_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    product = create_product(db, product_in)
    return product


@app.get("/products", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    products = get_products(db)
    return products

