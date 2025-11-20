from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import app.db

from app.database import SessionLocal
from app.models import Product
from app.schemas import ProductCreate, ProductRead
from app.crud import create_product, get_products
from app.scraper import scrape_price
from fastapi import HTTPException
from app.models import PriceHistory
from apscheduler.schedulers.background import BackgroundScheduler
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

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

@app.get("/products/{id}/check-price")
def check_price(id: int, db: Session = Depends(get_db)):
    product=db.query(Product).filter(Product.id==id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    price = scrape_price(product.url)
    if price is None:
        raise HTTPException(status_code=400, detail="Cannot extract price from page")
    history_entry = PriceHistory(
        product_id=id,
        price=price
    )
    db.add(history_entry)
    db.commit()
    return {
        "product_id": id,
        "name": product.name,
        "url": product.url,
        "current_price": price
    }
@app.get("/products/{id}/history")
def price_history(id: int, db: Session = Depends(get_db)):
    history = db.query(PriceHistory).filter(PriceHistory.product_id == id).all()
    return [
        {"price": h.price, "checked_at": h.checked_at}
        for h in history
    ]


def scheduled_price_check():
    logger.info("Starting scheduled price check...")

    db = SessionLocal()

    try:
        products = db.query(Product).all()

        for product in products:
            try:
                price = scrape_price(product.url)

                if price is None:
                    logger.warning(f"No price found for product ID {product.id}")
                    continue

                history = PriceHistory(
                    product_id=product.id,
                    price=price
                )
                db.add(history)
                db.commit()

                logger.info(f"Saved price {price} for product ID {product.id}")

            except Exception as e:
                logger.error(f"Error while processing product {product.id}: {e}")

    except Exception as e:
        logger.error(f"Error during main scheduler loop: {e}")

    finally:
        db.close()
        logger.info("Scheduled price check finished.")


@app.on_event("startup")
def start_scheduler():
    logger.info("Starting APScheduler...")
    scheduler.add_job(
        scheduled_price_check,
        "interval",
        minutes=60,   # potem zmienimy na 1h
        id="price_checker",
        replace_existing=True
    )
    scheduler.start()
    logger.info("APScheduler started.")

@app.on_event("shutdown")
def shutdown_scheduler():
    logger.info("Shutting down APScheduler...")
    scheduler.shutdown()
    logger.info("APScheduler shut down.")

@app.get("/run-scheduler-once")
def run_scheduler_once():
    scheduled_price_check()
    return {"status": "manual scheduler run complete"}
