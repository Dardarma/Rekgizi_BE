from typing import Optional
from sqlalchemy.orm import Session
from datetime import date, timedelta, time as dt_time
from fastapi import HTTPException
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.jadwal_libur import JadwalLibur
from app.models.jadwal_tersedia import JadwalTersedia
from app.schemas.jadwal_libur import JadwalLiburCreate
from app.utils.helpers.days import mapping_hari



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
        }
        for row in libur
    ]


def create_jadwal_libur_service(
        db: Optional[Session] = None,
        data: JadwalLiburCreate = None,
        user_id: int | None = None,
):
    Session = db or SessionLocal()

    start_date = data.tanggal_mulai or data.tanggal
    end_date = data.tanggal_selesai or data.tanggal_mulai or data.tanggal

    if start_date is None or end_date is None:
        raise HTTPException(
            status_code=400,
            detail="Tanggal libur wajib diisi"
        )

    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Tanggal mulai tidak boleh lebih besar dari tanggal selesai"
        )

    if start_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Tanggal libur tidak boleh kurang dari hari ini"
        )

    schedules_query = Session.query(JadwalTersedia).filter(
        JadwalTersedia.deleted_at.is_(None)
    )
    if user_id is not None:
        schedules_query = schedules_query.filter(JadwalTersedia.konselor_id == user_id)
    if data.jadwal_tersedia_id is not None:
        schedules_query = schedules_query.filter(JadwalTersedia.id == data.jadwal_tersedia_id)
    if data.start_time is not None or data.end_time is not None:
        if data.start_time is None or data.end_time is None:
            raise HTTPException(
                status_code=400,
                detail="Jam mulai dan jam selesai wajib diisi"
            )
        if data.start_time >= data.end_time:
            raise HTTPException(
                status_code=400,
                detail="Jam mulai harus sebelum jam selesai"
            )
        schedules_query = schedules_query.filter(
            JadwalTersedia.start_time < data.end_time,
            JadwalTersedia.end_time > data.start_time,
        )

    schedules = schedules_query.all()
    if not schedules:
        raise HTTPException(status_code=404, detail="Jadwal tersedia tidak ditemukan")

    schedules_by_day: dict[str, list[JadwalTersedia]] = {}
    for schedule in schedules:
        schedules_by_day.setdefault(str(schedule.day_of_week).strip().lower(), []).append(schedule)

    created_or_existing_ids: list[int] = []
    current_date = start_date
    while current_date <= end_date:
        day_key = mapping_hari(current_date.weekday())
        for schedule in schedules_by_day.get(day_key, []):
            existing = (
                Session.query(JadwalLibur)
                .filter(
                    JadwalLibur.jadwal_tersedia_id == schedule.id,
                    JadwalLibur.tanggal == current_date,
                )
                .first()
            )
            if existing:
                existing.deleted_at = None
                created_or_existing_ids.append(existing.id)
                continue

            new_libur = JadwalLibur(
                jadwal_tersedia_id=schedule.id,
                tanggal=current_date,
            )
            Session.add(new_libur)
            Session.flush()
            created_or_existing_ids.append(new_libur.id)

        current_date += timedelta(days=1)

    if not created_or_existing_ids:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada jadwal tersedia yang sesuai dengan rentang tanggal"
        )

    Session.commit()

    rows = (
        Session.query(
            JadwalLibur.id,
            JadwalLibur.jadwal_tersedia_id,
            JadwalLibur.tanggal,
            JadwalTersedia.end_time.label("end_time"),
            JadwalTersedia.start_time.label("start_time"),
            JadwalTersedia.day_of_week.label("day_of_week"),
        )
        .join(JadwalTersedia, JadwalLibur.jadwal_tersedia_id == JadwalTersedia.id)
        .filter(JadwalLibur.id.in_(created_or_existing_ids))
        .order_by(JadwalLibur.tanggal, JadwalTersedia.start_time)
        .all()
    )

    return [
        {
            "id": row.id,
            "jadwal_tersedia": row.jadwal_tersedia_id,
            "tanggal": row.tanggal,
            "end_time": _time_to_hhmm(row.end_time),
            "start_time": _time_to_hhmm(row.start_time),
            "day_of_week": row.day_of_week,
        }
        for row in rows
    ]

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
    




