from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import re 
from backend.config import settings
# Secret keys for JWT - in production, use environment variables
SECRET_KEY = "your-secret-key-change-in-production"
REFRESH_SECRET_KEY = "your-refresh-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# In-memory user storage (replace with database in production)
users_db = {}
# In-memory refresh token storage (replace with DB in production)
refresh_tokens_db = {}

# =========================
# Pydantic Models
# =========================
class User(BaseModel):
    username: str
    email: str
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None


# =========================
# Password Handling
# =========================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)



# =========================
# JWT Token Creation
# =========================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# =========================
# Get Current User (Protected Routes)
# =========================
async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError:
        # ✅ Improved error clarity
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username


# =========================
# Register User
# =========================
def register_user(username: str, email: str, password: str) -> dict:
    if username in users_db:
        return {"success": False, "message": "Username already exists"}
    if any(u.get("email") == email for u in users_db.values()):
        return {"success": False, "message": "Email already registered"}
    hashed_password = get_password_hash(password)
    users_db[username] = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password
    }
    # Remove any old refresh tokens for this user
    refresh_tokens_db.pop(username, None)
    return {"success": True, "message": "User registered successfully"}


# =========================
# Authenticate User (Login)
# =========================
def authenticate_user(username: str, password: str) -> Optional[str]:
    user = users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return username


# =========================
# Refresh Token Logic
# =========================
def store_refresh_token(username: str, refresh_token: str):
    refresh_tokens_db[username] = refresh_token

def verify_refresh_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        # Check if token matches stored one
        if refresh_tokens_db.get(username) != token:
            return None
        return username
    except JWTError:
        return None