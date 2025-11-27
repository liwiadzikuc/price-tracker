from sqlalchemy.orm import Session
from app.models import Product, User
from app.schemas import ProductCreate, ProductUpdate, UserCreate

def create_user(db: Session, user_in: UserCreate):
    user = User(email=user_in.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
    
def get_user_email(db: Session, user_id: int) -> str | None:
    return db.query(User.email).filter(User.id == user_id).scalar()

def create_product(db: Session, product_in: ProductCreate):
    product = Product(
        name=product_in.name,
        url=product_in.url,
        target_price=product_in.target_price,
        user_id=product_in.user_id
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