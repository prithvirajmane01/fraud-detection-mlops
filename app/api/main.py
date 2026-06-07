from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import os

# Create the FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection using a Random Forest model",
    version="1"
)

# Load the trained model using absolute path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model = joblib.load(os.path.join(BASE_DIR, "model", "fraud_model.pkl"))

# Define what a transaction looks like
class Transaction(BaseModel):
    transaction_amount: float
    transaction_hour: int
    days_since_last_transaction: int
    customer_age: int
    is_foreign_transaction: int
    num_transactions_today: int

# Health check endpoint
@app.get("/")
def health_check():
    return {"status": "Fraud Detection API is running"}

# Prediction endpoint
@app.post("/predict")
def predict(transaction: Transaction):
    features = np.array([[
        transaction.transaction_amount,
        transaction.transaction_hour,
        transaction.days_since_last_transaction,
        transaction.customer_age,
        transaction.is_foreign_transaction,
        transaction.num_transactions_today
    ]])

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    return {
        "prediction": int(prediction),
        "fraud_probability": round(float(probability), 4),
        "verdict": "FRAUD" if prediction == 1 else "LEGITIMATE"
    }