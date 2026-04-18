from typing import Optional
from sqlalchemy.orm import Session
from datetime import date, timedelta, time as dt_time
from fastapi import HTTPException
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.jadwal_libur import JadwalLibur
from app.models.jadwal_tersedia import JadwalTersedia
from app.schemas.jadwal_libur import JadwalLiburCreate



def _time_to_hhmm(value: dt_time | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%H:%M")


def get_jadwal_libur_by_id_orm(
        db: Optional[Session] = None,
        jadwal_libur_id: int = None
):
    Session = db or SessionLocal()

    jadwal_libur = Session.query(JadwalLibur).filter(
        JadwalLibur.id == jadwal_libur_id,
        JadwalLibur.deleted_at.is_(None)
    ).first()

    return jadwal_libur

def get_jadwal_libur_read(
     db: Optional[Session] = None,
     jadwal_libur_id: int | None = None,
):
    Session = db or SessionLocal()

    jadwal_libur = (
        Session.query(
            JadwalLibur.id,
            JadwalLibur.jadwal_tersedia_id,
            JadwalLibur.tanggal,
            JadwalLibur.deleted_at.label("deleted_at"),
            JadwalTersedia.end_time.label("end_time"),
            JadwalTersedia.start_time.label("start_time"),
            JadwalTersedia.day_of_week.label("day_of_week"),
        )
        .join(JadwalTersedia, JadwalLibur.jadwal_tersedia_id == JadwalTersedia.id)
        .filter(JadwalLibur.id == jadwal_libur_id)
    )
    
    jadwal_libur = jadwal_libur.first()

    return jadwal_libur

def get_jadwal_libur_service(
        db: Optional[Session] = None,
        user_id: int = None,
        start_date: date = None,
        end_date: date = None
):
    if start_date is None:
        start_date = date.today()
    
    if end_date is None:
        end_date = start_date + timedelta(days=30)

    Session = db or SessionLocal()

    libur = (Session.query(
        JadwalLibur.id,
        JadwalLibur.jadwal_tersedia_id,
        JadwalLibur.tanggal,
        JadwalTersedia.end_time.label("end_time"),
        JadwalTersedia.start_time.label("start_time"),
        JadwalTersedia.day_of_week.label("day_of_week"),
    )
    .join(JadwalTersedia, JadwalLibur.jadwal_tersedia_id == JadwalTersedia.id)
    .filter(JadwalLibur.deleted_at.is_(None))
    .filter(JadwalLibur.tanggal.between(start_date, end_date))
    .filter(JadwalTersedia.konselor_id == user_id)
    ).all()


    return[ 
        {
            "id": row.id,
            "jadwal_tersedia": row.jadwal_tersedia_id,
            "tanggal": row.tanggal,
            "end_time": _time_to_hhmm(row.end_time),
            "start_time": _time_to_hhmm(row.start_time),
            "day_of_week": row.day_of_week,
            "deleted_at": _time_to_hhmm(row.deleted_at)
        }
        for row in libur
    ]


def create_jadwal_libur_service(
        db: Optional[Session] = None,
        data: JadwalLiburCreate = None
):
    Session = db or SessionLocal()

    new_libur = JadwalLibur(
        jadwal_tersedia_id=data.jadwal_tersedia_id,
        tanggal=data.tanggal
    )
    Session.add(new_libur)
    Session.commit()
    Session.flush(new_libur)

    new_libur = get_jadwal_libur_read(db=Session, jadwal_libur_id=new_libur.id)

    return{
        "id": new_libur.id,
        "jadwal_tersedia": new_libur.jadwal_tersedia_id,
        "tanggal": new_libur.tanggal,
        "end_time": _time_to_hhmm(new_libur.end_time),
        "start_time": _time_to_hhmm(new_libur.start_time),
        "day_of_week": new_libur.day_of_week,
    }

def get_jadwal_libur_by_id_service(
        db: Optional[Session] = None,
        jadwal_libur_id: int = None
):
    Session = db or SessionLocal()
    jadwal_libur = get_jadwal_libur_read(Session, jadwal_libur_id=jadwal_libur_id)

    if jadwal_libur is None:
        return None

    return {
        "id": jadwal_libur.id,
        "jadwal_tersedia": jadwal_libur.jadwal_tersedia_id,
        "tanggal": jadwal_libur.tanggal,
        "end_time": _time_to_hhmm(jadwal_libur.end_time),
        "start_time": _time_to_hhmm(jadwal_libur.start_time),
        "day_of_week": jadwal_libur.day_of_week,
    }

def delete_jadwal_libur_service(
        db: Optional[Session] = None,
        jadwal_libur_id: int = None,
):
    Session = db or SessionLocal()

    jadwal_libur = get_jadwal_libur_by_id_orm(Session, jadwal_libur_id=jadwal_libur_id)
    if jadwal_libur is None:
        raise HTTPException(status_code=404, detail="Jadwal libur not found")
    
    jadwal_libur.deleted_at = func.now()

    Session.commit()
    Session.refresh(jadwal_libur)

    jadwal_libur = get_jadwal_libur_read(db=Session, jadwal_libur_id=jadwal_libur.id)
    return {
        "id": jadwal_libur.id,
        "jadwal_tersedia": jadwal_libur.jadwal_tersedia_id,
        "tanggal": jadwal_libur.tanggal,
        "end_time": _time_to_hhmm(jadwal_libur.end_time),
        "start_time": _time_to_hhmm(jadwal_libur.start_time),
        "day_of_week": jadwal_libur.day_of_week,
        "deleted_at":  _time_to_hhmm(jadwal_libur.deleted_at),
    }
    




