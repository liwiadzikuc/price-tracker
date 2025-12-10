from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
from random import randint
import app.db

from app.database import SessionLocal
from app.models import Product, PriceHistory, PriceAlert
from app.schemas import ProductCreate, ProductRead, ProductUpdate, UserCreate, UserRead, UserLogin, VerifyCode
from app.crud import create_product, get_products, update_product, delete_product, create_user, get_user_by_id,get_user_email,get_user_by_email,verify_user, set_verification_code
from app.scraper import scrape_price_async, scrape_price
from apscheduler.schedulers.background import BackgroundScheduler
from app.mailer import send_price_alert_email, send_verification_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

app = FastAPI()

#cors - frontend gada z api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok"}

# @app.post("/users", response_model=UserRead)
# def add_user(user_in: UserCreate, db: Session = Depends(get_db)):
#     #w przyszlosci logowanie/rejestracja, chwilowo user zawsze nowu
#     user = create_user(db, user_in)
#     return user

# @app.get("/users/{id}", response_model=UserRead)
# def get_user(id: int, db: Session = Depends(get_db)):
#     user = get_user_by_id(db, id)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

@app.post("/register")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, user_in)
    code = str(randint(100000, 999999))
    set_verification_code(db, user, code)
    send_verification_email(user.email, code)
    return {"message": "Rejestracja udana, sprawdź email i wpisz kod weryfikacyjny."}

@app.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, user_in.email)
    if not user or user.password != user_in.password:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Account not verified")

    return {"user_id": user.id, "email": user.email}

@app.post("/verify")
def verify(data: VerifyCode, db: Session = Depends(get_db)):
    user = verify_user(db, data.email, data.code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid code or email")

    return {"message": "Konto zweryfikowane! Możesz się teraz zalogować."}

@app.post("/products", response_model=ProductRead)
def add_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    if not get_user_by_id(db, product_in.user_id):
        raise HTTPException(status_code=404, detail=f"User with ID {product_in.user_id} not found")
    product = create_product(db, product_in)
    return product


@app.get("/products/{user_id}", response_model=list[ProductRead])
def list_products(user_id: int,db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.user_id == user_id).all()

@app.put("/products/{id}", response_model=ProductRead) 
def edit_product(id: int, product_in: ProductUpdate, db: Session = Depends(get_db)):
    product = update_product(db, id, product_in)

    if product is None:
        raise HTTPException(status_code=404, detail=f"Product with ID {id} not found")

    return product
@app.delete("/products/{id}") 
def remove_product(id: int, db: Session = Depends(get_db)):
    result = delete_product(db, id)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Product with ID {id} not found")

    return result

@app.get("/products/{id}/check-price")
async def check_price(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    price = await scrape_price_async(product.url)

    if price is None:
        raise HTTPException(status_code=400, detail="Cannot extract price from page")

    if price <= product.target_price:
        alert = PriceAlert(product_id=id, price=price)
        db.add(alert)
        recipient_email = get_user_email(db, product.user_id)
        if recipient_email:
            send_price_alert_email(
                recipient_email=recipient_email,
                product_name=product.name,
                price=price,
                target_price=product.target_price,
                product_url=product.url
            )
        logger.info(f"ALERT! Price dropped for product {product.id}: {price}")

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


# schedulert
def scheduled_price_check():
    logger.info("Starting scheduled price check...")
    db = SessionLocal()
    try:
        products = db.query(Product).all()

        for product in products:
            try:
                price = scrape_price(product.url)  # sync wrapper

                if price is None:
                    logger.warning(f"No price found for product ID {product.id}")
                    continue

                history = PriceHistory(
                    product_id=product.id,
                    price=price
                )
                db.add(history)
                db.commit()

                if price <= product.target_price:
                    alert = PriceAlert(product_id=product.id, price=price)
                    db.add(alert)
                    send_price_alert_email(
                        product_name=product.name,
                        price=price,
                        target_price=product.target_price,
                        product_url=product.url
                    )
                    logger.info(f"ALERT! Price dropped for product {product.id}: {price}")

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
        minutes=60,
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


@app.get("/products/{id}/alerts")
def product_alerts(id: int, db: Session = Depends(get_db)):
    alerts = db.query(PriceAlert).filter(PriceAlert.product_id == id).all()
    return [
        {
            "id": a.id,
            "price": a.price,
            "created_at": a.created_at
        }
        for a in alerts
    ]

