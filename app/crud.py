from sqlalchemy.orm import Session
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate


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

def update_product(db: Session,product_id: int, product_in: ProductUpdate):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    update_data = product_in.model_dump(exclude_unset=True) # exclude_unset=True pominiecie pol ktorych nie ma w zadaniu
    for key, value in update_data.items():
        setattr(product, key, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    db.delete(product)
    db.commit()
    return {"message": f"Product with ID {product_id} deleted successfully"}