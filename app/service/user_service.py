from datetime import datetime, timezone
from math import ceil
from typing import Any, Dict, List, Optional
from fastapi import HTTPException

from sqlalchemy import String, and_, cast, or_
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import User
from app.schemas.userSchema import UserBase, UserSearchRequest, UserUpdate
from app.core.security import hash_password


def get_all_users(
    db:Session,
    user_search: UserSearchRequest,
    only_pasien: bool =False
):
    tokens = user_search.search.lower().split()
    
    filters = []
    
    for token in tokens:
        filters.append(
           or_(
                User.nama.ilike(f"%{token}%"),
                User.email.ilike(f"%{token}%"),
                cast(User.role, String).ilike(f"%{token}%"),
               
                User.alamat["desa"].astext.ilike(f"%{token}%"),
                User.alamat["kecamatan"].astext.ilike(f"%{token}%"),
                User.alamat["kabupaten"].astext.ilike(f"%{token}%"),
                User.alamat["provinsi"].astext.ilike(f"%{token}%"),
                
                cast(User.tanggal_lahir, String).ilike(f"%{token}%"),
           ) 
        )
        
    base_query = (
        db.query(User).filter(
            User.deleted_at.is_(None),
            and_(*filters),
        )
    )
    
    if only_pasien:
        base_query = base_query.filter(User.role == "pasien")
    
    total = base_query.count()
    
    limit = user_search.limit
    current_page = user_search.current_page
    offset = (current_page - 1) * limit
    
    users = base_query.offset(offset).limit(limit).all()
    
    total_pages = ceil(total / limit) if limit > 0 else 1
    
    return {
        "meta": {
            "current_page": current_page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        },
        "data": users
    }

def get_user_by_id(user_id: int, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
	owns_session = db is None
	session = db or SessionLocal()

	try:
		row = (
			session.query(
				User.id,
				User.role,
				User.nama,
				User.jenis_kelamin,
				User.alamat,
				User.tanggal_lahir,
				User.email,
			)
			.filter(User.id == user_id)
			.filter(User.deleted_at.is_(None))
			.first()
		)
		if row is None:
			raise HTTPException(status_code=404, detail="User not found")
		return {
			"id": row.id,
			"role": getattr(row.role, "value", row.role),
			"nama": row.nama,
			"jenis_kelamin": row.jenis_kelamin,
			"alamat": row.alamat,
			"tanggal_lahir": row.tanggal_lahir,
			"email": row.email,
		}
	
	finally:
		if owns_session:
			session.close()

def create_user_service(
		user_data: UserBase,
		db: Optional[Session] = None,
		*,
		force_role: str | None = None,
):
	owns_session = db is None
	session = db or SessionLocal()

	try:
		if user_data.email:
			existing_user = session.query(User).filter(User.email == user_data.email).first()
			if existing_user:
				raise HTTPException(
					status_code=400,
					detail="Email sudah terdaftar",
				)

		role = force_role or getattr(user_data, "role", None) or "pasien"

		user = User(
			role = role,
			nama = user_data.nama,
			jenis_kelamin = user_data.jenis_kelamin,
			alamat = user_data.alamat.model_dump() if user_data.alamat else None,
			tanggal_lahir = user_data.tanggal_lahir,
			email = user_data.email,
			pass_hash = hash_password(user_data.password),

			created_at = datetime.now(timezone.utc),
			updated_at = datetime.now(timezone.utc),
		)

		session.add(user)
		session.commit()
		session.refresh(user)

		return {
			"id": user.id,
			"role" : getattr(user.role, "value", user.role),
			"nama" : user.nama,
			"jenis_kelamin" : user.jenis_kelamin,
			"alamat" : user.alamat,
			"tanggal_lahir" : user.tanggal_lahir,
			"email" : user.email,
		}
	except Exception :
		session.rollback()
		raise
	finally:
		if owns_session:
			session.close()

def edit_user_service(
	user_id: int,
	user_data: UserUpdate,
	db: Session,
):
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise HTTPException(
			status_code=404,
			detail="User not found"
		)
	if user_data.email:
		existing_user = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
		if existing_user:
			raise HTTPException(
				status_code=400,
				detail="Email sudah terdaftar",
			)
	
	update_data = user_data.model_dump(exclude_unset=True)
 
	password = update_data.pop("password", None)

	if password:
		user.password = hash_password(password)
    
	for field, value in update_data.items():
		setattr(user, field, value)
  
	db.commit()
	db.refresh(user)

	return {
		"id": user.id,
		"role" : getattr(user.role, "value", user.role),
		"nama" : user.nama,
		"jenis_kelamin" : user.jenis_kelamin,
		"alamat" : user.alamat,
		"tanggal_lahir" : user.tanggal_lahir,
	}

def delete_user_service(
		user_id: int,
		db: Session,
):
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		return None
	user.deleted_at = datetime.now(timezone.utc)
	db.commit()
	db.refresh(user)
	return {
		"id": user.id,
		"role" : getattr(user.role, "value", user.role),
		"nama" : user.nama,
		"jenis_kelamin" : user.jenis_kelamin,
		"alamat" : user.alamat,
		"tanggal_lahir" : user.tanggal_lahir,
		"deleted_at" : user.deleted_at,
	}

