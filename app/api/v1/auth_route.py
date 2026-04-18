from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth_schema import LoginSchema, TokenSchema
from app.utils.helpers.respons import APIResponse
from app.core.database import SessionLocal
from app.schemas.userSchema import UserBase, UserBasicInfo, UserRegister

from app.service.auth_service import authenticate_user, register_user

router = APIRouter( tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=APIResponse[TokenSchema], summary="Login user and get access token")
def login(
    data: LoginSchema,
    db: Session = Depends(get_db),
):
    result = authenticate_user(
        db = db,
        email = data.email,
        password= data.password
    )

    return APIResponse(
        status_code=200,
        message="Login successful",
        data=result
    )

@router.post("/register", response_model=APIResponse[UserBasicInfo], summary="Register new user")
def register(
    data: UserBase,
    db : Session = Depends(get_db)
):
    user = register_user( user_data=data, db=db)
    return APIResponse(
        status_code=201,
        message="user Berhasil dibuat",
        data=user
    )
    
   
    