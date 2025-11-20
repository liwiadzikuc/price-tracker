from app.database import Base, engine
from app.models import Product, PriceHistory

Base.metadata.create_all(bind=engine)
