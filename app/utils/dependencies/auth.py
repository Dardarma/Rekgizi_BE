from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jst,JWTError
from app.core.config import ALGORITHM
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="/api/v1/login")

def get_current_payload(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="token tidak valid"
        )