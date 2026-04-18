from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str,hashed: str) -> bool :
    return pwd_context.verify(plain_password, hashed) 

def create_access_token(data: dict, expires_delta: timedelta | None = None):  
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = data.copy()
    to_encode.update({
        "iat": now,
        "exp": expire,
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
