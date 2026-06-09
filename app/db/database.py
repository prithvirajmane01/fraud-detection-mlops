from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
import os

# Load database URL from root config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Predictions table definition
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_amount = Column(Float)
    transaction_hour = Column(Integer)
    days_since_last_transaction = Column(Integer)
    customer_age = Column(Integer)
    is_foreign_transaction = Column(Integer)
    num_transactions_today = Column(Integer)
    prediction = Column(Integer)
    fraud_probability = Column(Float)
    verdict = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()