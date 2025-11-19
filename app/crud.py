from sqlalchemy.orm import Session
from app.models import Product
from app.schemas import ProductCreate


def create_product(db: Session, product_in: ProductCreate):
    product = Product(
        name=product_in.name,
        url=product_in.url,
        target_price=product_in.target_price
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_products(db: Session):
    return db.query(Product).all()
