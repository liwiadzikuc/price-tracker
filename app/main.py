from fastapi import FastAPI
from sqlalchemy import text
from app.db import SessionLocal, TestTable

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/test-db")
def test_db():
    db = SessionLocal()
    try:
        row = TestTable(message="działa")
        db.add(row)
        db.commit()
        db.refresh(row)

        return {"database": "ok", "saved_message": row.message}
    except Exception as e:
        return {"database": "error", "details": str(e)}
    finally:
        db.close()
