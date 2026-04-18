from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.models.users import User
from fastapi import HTTPException

from app.schemas.userSchema import UserBase
from app.service.user_service import create_user_service

def authenticate_user(db:Session,email:str, password:str):
    user = db.query(User).filter(
        User.email == email,
        User.deleted_at.is_(None)
        ).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="email tidak ditemukan"
        )
    if verify_password(password, user.pass_hash) is False:
        raise HTTPException(
            status_code=401,
            detail="password salah"
        )
    token = create_access_token({
        "sub": str(user.id),
        "role": getattr(user.role, "value", user.role)
        })
    return {
        "access_token" : token,
        "token_type" : "bearer",
        "user" : {
            "id": user.id,
            "nama": user.nama,
            "email": user.email,
            "role": user.role
        }
    }

def register_user(
        user_data: UserBase,
        db: Optional[Session] = None
):
    return create_user_service(
        user_data=user_data,
        db=db,
        force_role="pasien"
    )

