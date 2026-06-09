from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# ─────────────────────────────────────────────
# Security configuration
# SECRET_KEY is used to sign tokens — keep this private
# ─────────────────────────────────────────────
SECRET_KEY = "fraud-detection-super-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This tells FastAPI where clients send their token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ─────────────────────────────────────────────
# Fake user database
# In production this would be a real database table
# ─────────────────────────────────────────────
FAKE_USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("secret123"),
        "role": "admin"
    }
}

# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = FAKE_USERS.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username