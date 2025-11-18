from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TestTable(Base):
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)

Base.metadata.create_all(bind=engine)