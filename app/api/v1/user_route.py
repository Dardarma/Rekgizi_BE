from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.userSchema import UserBasicInfo, UserCreate, UserSearchRequest, UserUpdate, userResponseAPI
from app.utils.helpers.respons import APIResponse
from app.core.database import SessionLocal
from app.service.user_service import delete_user_service, edit_user_service, get_all_users, get_user_by_id,create_user_service


router = APIRouter(prefix="/users", tags=["users"])

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

@router.get("/", response_model=APIResponse[userResponseAPI], summary="Search Asuhan user")
def get_asuhan_search(
    db: Session = Depends(get_db),
    user_request_schema: UserSearchRequest = Depends(),
    only_pasien: bool = False,
    _: None = Depends(require_role(RoleEnum.admin))
):
    user = get_all_users(db,user_request_schema,only_pasien)
    
    return APIResponse(
        status_code=200,
        message="success",
        data = user
    )

@router.get("/{user_id}", response_model=APIResponse[UserBasicInfo], summary="Get user info by ID")
def get_user(user_id: int, 
             db: Session = Depends(get_db),
             _: None = Depends(require_role(RoleEnum.admin))):
	user = get_user_by_id(user_id, db)
	return APIResponse(
		status_code=200, 
		message="Success", 
		data=user
	)

@router.post("/",response_model=APIResponse[UserBasicInfo], summary="Create a new user")
def create_user(
	payload: UserCreate,
	db: Session = Depends(get_db),
	_: None = Depends(require_role(RoleEnum.admin))
):
	user = create_user_service(payload,db)
	if user is None:
		raise HTTPException(
			status_code=400, 
			detail="Failed to create user"
		)
	return APIResponse(
		status_code=201, 
		message="User created successfully", 
		data=user
	)

@router.patch("/{user_id}" , response_model=APIResponse[UserBasicInfo], summary="Update user info by ID")
def update_user(
	user_id : int,
	payload: UserUpdate,
	db: Session = Depends(get_db),
	_: None = Depends(require_role(RoleEnum.admin))
):
	user = edit_user_service(user_id, payload, db)

	if user is None:
		raise HTTPException(
			status_code=404, 
			detail="User not found"
		)
	return APIResponse(
		status_code=200, 
		message="User updated successfully", 
		data=user
	)

@router.patch("/delete/{user_id}", response_model=APIResponse[UserBasicInfo], summary="Soft delete user by ID")
def delete_user(
	user_id: int,
	db: Session = Depends(get_db),
	_: None = Depends(require_role(RoleEnum.admin))
):
	user = delete_user_service(user_id, db)

	if user is None:
		raise HTTPException(
			status_code=404, 
			detail="User not found"
		)
	return APIResponse(
		status_code=200, 
		message="User deleted successfully", 
		data=user
	)
 
 