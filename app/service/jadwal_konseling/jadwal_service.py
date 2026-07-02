from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.core.database import SessionLocal
from app.models import JadwalKonseling, User, JadwalTersedia
from app.models.jadwal_konseling import statusEnum
from app.schemas.jadwal_schema import jadwalKonselingCreate, jadwalKonselingUpdate
from app.service.notification_service import send_jadwal_konseling_notification

def get_jadwal_kosultasi_by_user(
        db: Optional[Session] = None, 
        user_id: int = None, role: str = None,
        page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
    owns_session = db is None
    session = db or SessionLocal()
    konselor = aliased(User)
    pasien = aliased(User)

    try:
        jadwal = (
            session.query(
            JadwalKonseling.id,
            JadwalKonseling.pasien_id,
            JadwalKonseling.konselor_id,
            JadwalKonseling.jadwal_tersedia_id,
            JadwalKonseling.tanggal_konseling,
            JadwalKonseling.status,
            JadwalKonseling.catatan,
            konselor.nama.label("nama_konselor"),
            pasien.nama.label("nama_pasien"),
            JadwalTersedia.start_time,
            JadwalTersedia.end_time,
            JadwalTersedia.day_of_week,
            )
            .filter(JadwalKonseling.deleted_at.is_(None))
            .join(konselor, JadwalKonseling.konselor_id == konselor.id)
            .join(pasien, JadwalKonseling.pasien_id == pasien.id)
            .join(JadwalTersedia, JadwalKonseling.jadwal_tersedia_id == JadwalTersedia.id)
        )

        if role == "ahli_gizi":
            jadwal = jadwal.filter(JadwalKonseling.konselor_id == user_id)
        elif role == "pasien":
            jadwal = jadwal.filter(JadwalKonseling.pasien_id == user_id)
        else:
            raise HTTPException(
                status_code=403,
                detail="maaf anda tidak memiliki akses"
            )

        total = jadwal.count()
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        jadwal = jadwal.offset((page - 1) * limit).limit(limit).all()

        if not jadwal and page == 1:
            raise HTTPException(
                status_code=404,
                detail="Jadwal tidak ditemukan"
            )

        return {
            "data": [
                {
                    "id": item.id,
                    "pasien_id": item.pasien_id,
                    "konselor_id": item.konselor_id,
                    "jadwal_tersedia_id": item.jadwal_tersedia_id,
                    "tanggal_konseling": item.tanggal_konseling,
                    "nama_konselor": item.nama_konselor,
                    "nama_pasien": item.nama_pasien,
                    "day_of_week": item.day_of_week,
                    "start_time": item.start_time,
                    "end_time": item.end_time,
                    "status": item.status,
                    "catatan": item.catatan,
                }
                for item in jadwal
            ],
            "total": total,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit
        }
    finally:
        if owns_session:
            session.close()

def get_jadwal_konsultasi_orm(
    db: Session,
    jadwal_konseling_id: int | None = None
):
    query = db.query(JadwalKonseling).filter(JadwalKonseling.deleted_at.is_(None))

    if jadwal_konseling_id is None:
        return query.all()

    return query.filter(JadwalKonseling.id == jadwal_konseling_id).first()

def get_jadwal_konsultasi_read(
    db: Session,
    jadwal_konseling_id: int | None = None
):
    konselor = aliased(User)
    pasien = aliased(User)
    jadwal = (
        db.query(
        JadwalKonseling.id,
        JadwalKonseling.pasien_id,
        JadwalKonseling.konselor_id,
        JadwalKonseling.jadwal_tersedia_id,
        JadwalKonseling.tanggal_konseling,
        JadwalKonseling.status,
        JadwalKonseling.catatan,
        konselor.nama.label("nama_konselor"),
        pasien.nama.label("nama_pasien"),
        JadwalTersedia.start_time,
        JadwalTersedia.end_time,
        JadwalTersedia.day_of_week,
        )
        .filter(JadwalKonseling.deleted_at.is_(None))
        .join(konselor, JadwalKonseling.konselor_id == konselor.id)
        .join(pasien, JadwalKonseling.pasien_id == pasien.id)
        .join(JadwalTersedia, JadwalKonseling.jadwal_tersedia_id == JadwalTersedia.id)
    )

    if jadwal_konseling_id is None:
        return jadwal.all()

    return jadwal.filter(JadwalKonseling.id == jadwal_konseling_id).first()

def get_jadwal_konsultasi_by_id_service(
    db: Session,
    jadwal_konseling_id: int | None = None
):
    jadwal_konseling = get_jadwal_konsultasi_read(db=db, jadwal_konseling_id=jadwal_konseling_id)

    return{
        "id": jadwal_konseling.id,
        "pasien_id": jadwal_konseling.pasien_id,
        "konselor_id": jadwal_konseling.konselor_id,
        "jadwal_tersedia_id": jadwal_konseling.jadwal_tersedia_id,
        "tanggal_konseling": jadwal_konseling.tanggal_konseling,
        "nama_konselor": jadwal_konseling.nama_konselor,
        "nama_pasien": jadwal_konseling.nama_pasien,
        "day_of_week": jadwal_konseling.day_of_week,
        "start_time": jadwal_konseling.start_time,
        "end_time": jadwal_konseling.end_time,
        "status": jadwal_konseling.status,
        "catatan": jadwal_konseling.catatan,
    }

def create_jadwal_konseling_service(
    db: Session,
    payload: jadwalKonselingCreate,
    pasien_id: int,
):
    existing_jadwal = (
        db.query(JadwalKonseling)
        .filter(
            JadwalKonseling.deleted_at.is_(None),
            JadwalKonseling.pasien_id == pasien_id,
            JadwalKonseling.konselor_id == payload.konselor_id,
            JadwalKonseling.jadwal_tersedia_id == payload.jadwal_tersedia_id,
            JadwalKonseling.tanggal_konseling == payload.tanggal_konseling,
            JadwalKonseling.status.in_([statusEnum.pending, statusEnum.approved]),
        )
        .first()
    )

    if existing_jadwal:
        raise HTTPException(
            status_code=409,
            detail="Anda sudah mengajukan jadwal konsultasi untuk konselor, tanggal, dan jam yang sama",
        )

    new_jadwal_konseling = JadwalKonseling(
        pasien_id=pasien_id,
        konselor_id=payload.konselor_id,
        jadwal_tersedia_id=payload.jadwal_tersedia_id,
        tanggal_konseling=payload.tanggal_konseling,
        status="pending",
        catatan=payload.catatan
    )
    db.add(new_jadwal_konseling)
    db.commit()
    db.refresh(new_jadwal_konseling)

    new_jadwal_konseling = get_jadwal_konsultasi_read(db=db, jadwal_konseling_id=new_jadwal_konseling.id)
    send_jadwal_konseling_notification(db, new_jadwal_konseling)

    return{
        "id": new_jadwal_konseling.id,
        "pasien_id": new_jadwal_konseling.pasien_id,
        "konselor_id": new_jadwal_konseling.konselor_id,
        "jadwal_tersedia_id": new_jadwal_konseling.jadwal_tersedia_id,
        "tanggal_konseling": new_jadwal_konseling.tanggal_konseling,
        "nama_konselor": new_jadwal_konseling.nama_konselor,
        "nama_pasien": new_jadwal_konseling.nama_pasien,
        "day_of_week": new_jadwal_konseling.day_of_week,
        "start_time": new_jadwal_konseling.start_time,
        "end_time": new_jadwal_konseling.end_time,
        "status": new_jadwal_konseling.status,
        "catatan": new_jadwal_konseling.catatan,
    }

def edit_jadwal_konseling_service(
    db: Session,
    jadwal_konseling_id: int,
    payload: jadwalKonselingUpdate,
):
    jadwal = get_jadwal_konsultasi_orm(db=db, jadwal_konseling_id=jadwal_konseling_id)

    if not jadwal:
        raise HTTPException(status_code=404, detail="Jadwal Konseling tidak ditemukan")

    if payload.status == 'approved':
        raise HTTPException(status_code=400, detail="Jadwal disetujui tidak dapat diubah hanya bisa dihapus")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(jadwal, field, value)

    db.commit()
    db.refresh(jadwal)

    updated_jadwal = get_jadwal_konsultasi_read(db=db, jadwal_konseling_id=jadwal.id)
    return{
        "id": updated_jadwal.id,
        "pasien_id": updated_jadwal.pasien_id,
        "konselor_id": updated_jadwal.konselor_id,
        "jadwal_tersedia_id": updated_jadwal.jadwal_tersedia_id,
        "tanggal_konseling": updated_jadwal.tanggal_konseling,
        "nama_konselor": updated_jadwal.nama_konselor,
        "nama_pasien": updated_jadwal.nama_pasien,
        "day_of_week": updated_jadwal.day_of_week,
        "start_time": updated_jadwal.start_time,
        "end_time": updated_jadwal.end_time,
        "status": updated_jadwal.status,
        "catatan": updated_jadwal.catatan,
    }


def ubah_status_dan_catatan_jadwal_konseling_service(
    db: Session,
    jadwal_konseling_id: int,
    new_status: str | None = None,
    new_catatan: str | None = None,
):
    jadwal = get_jadwal_konsultasi_orm(db=db, jadwal_konseling_id=jadwal_konseling_id)

    if not jadwal:
        raise HTTPException(status_code=404, detail="Jadwal Konseling tidak ditemukan")

    if new_status is not None:
        if new_status not in ["pending", "approved", "rejected"]:
            raise HTTPException(status_code=400, detail="Status tidak valid")

        if jadwal.status == "approved" and new_status == "pending":
            raise HTTPException(status_code=400, detail="Status approved tidak dapat diubah kembali ke pending")

        jadwal.status = new_status

    if new_catatan is not None:
        jadwal.catatan = new_catatan

    db.commit()
    db.refresh(jadwal)

    updated_jadwal = get_jadwal_konsultasi_read(db=db, jadwal_konseling_id=jadwal.id)
    return{
        "id": updated_jadwal.id,
        "pasien_id": updated_jadwal.pasien_id,
        "konselor_id": updated_jadwal.konselor_id,
        "jadwal_tersedia_id": updated_jadwal.jadwal_tersedia_id,
        "tanggal_konseling": updated_jadwal.tanggal_konseling,
        "nama_konselor": updated_jadwal.nama_konselor,
        "nama_pasien": updated_jadwal.nama_pasien,
        "day_of_week": updated_jadwal.day_of_week,
        "start_time": updated_jadwal.start_time,
        "end_time": updated_jadwal.end_time,
        "status": updated_jadwal.status,
        "catatan": updated_jadwal.catatan,
    }
     
def delete_jadwal_konseling_service(
    db: Session,
    jadwal_konseling_id: int,
):
    jadwal = get_jadwal_konsultasi_orm(db=db, jadwal_konseling_id=jadwal_konseling_id)

    if not jadwal:
        raise HTTPException(status_code=404, detail="Jadwal Konseling tidak ditemukan")

    jadwal.deleted_at = func.now()

    db.commit()

    return {
        "message": "Jadwal Konseling berhasil dihapus"
    }



        
        
    
