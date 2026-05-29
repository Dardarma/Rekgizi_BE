from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.require_role import get_current_user
from app.models.rekam_pasien import RekamPasien
from app.models.users import RoleEnum

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

def can_access_rekam_pasien_summary(
    id_rekam_pasien: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if isinstance(current_user, dict):
        user_role = current_user.get("role")
        user_id = current_user.get("id")
    else:
        user_role = getattr(current_user, "role", None)
        user_id = getattr(current_user, "user_id", None) or getattr(current_user, "id", None)

    role_value = user_role.value if isinstance(user_role, RoleEnum) else str(user_role)

    if role_value in [
        RoleEnum.ahli_gizi.value,
        RoleEnum.tenaga_kesehatan.value
    ]:
        return current_user

    if role_value == RoleEnum.pasien.value:

        rekam_pasien = (
            db.query(RekamPasien)
            .filter(RekamPasien.id == id_rekam_pasien)
            .first()
        )

        if not rekam_pasien:
            raise HTTPException(
                status_code=404,
                detail="Rekam pasien tidak ditemukan"
            )

        if rekam_pasien.pasien_id != int(user_id):
            raise HTTPException(
                status_code=403,
                detail="Tidak memiliki akses"
            )

        return current_user

    raise HTTPException(
        status_code=403,
        detail="Role tidak diizinkan"
    )