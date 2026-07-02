from typing import  List, Optional
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.jadwal_tersedia import JadwalTersedia
from app.models.jadwal_libur import JadwalLibur
from app.models.users import User
from app.utils.helpers.days import mapping_hari
from app.schemas.jadwal_tersedia_schema import JadwalTersediaCreate, JadwalTersediaUpdate

def get_jadwal_tersedia_weekly(
    db: Optional[Session] = None,
):
    Session = db or SessionLocal()

    weekly_rows = (
        Session.query(
            JadwalTersedia.id,
            JadwalTersedia.konselor_id,
            User.nama.label("konselor_nama"),
            JadwalTersedia.day_of_week,
            JadwalTersedia.start_time,
            JadwalTersedia.end_time,
        ).filter(JadwalTersedia.deleted_at.is_(None))
        .join(User, User.id == JadwalTersedia.konselor_id)
    ).all()

    return [
        {
            "id": row.id,
            "konselor_id": row.konselor_id,
            "konselor_nama": row.konselor_nama,
            "day_of_week": row.day_of_week,
            "start_time": row.start_time,
            "end_time": row.end_time,
        }
        for row in weekly_rows
    ]


def get_jadwal_tersedia_by_user_service(
    db: Optional[Session] = None,
    user_id: int = None
):
    Session = db or SessionLocal()

    query = (
        Session.query(
            JadwalTersedia.id,
            JadwalTersedia.konselor_id,
            JadwalTersedia.day_of_week,
            JadwalTersedia.start_time,
            JadwalTersedia.end_time,
        ).filter(JadwalTersedia.deleted_at.is_(None))
        .filter(JadwalTersedia.konselor_id == user_id)
    ).all()

    return [
        {
            "id": row.id,
            "konselor_id": row.konselor_id,
            "day_of_week": row.day_of_week,
            "start_time": row.start_time,
            "end_time": row.end_time,
        }
        for row in query
    ]    

def get_libur(
        db: Optional[Session] = None,
        start_date: date = None,
        end_date: date = None
):
    Session = db or SessionLocal()

    libur_rows = (
        Session.query(JadwalLibur)
        .filter(JadwalLibur.deleted_at.is_(None))
        .filter(JadwalLibur.tanggal.between(start_date, end_date))
    ).all()

    return [
        {
            "id": row.id,
            "jadwal_tersedia_id": row.jadwal_tersedia_id,
            "tanggal": row.tanggal,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "deleted_at": row.deleted_at,
        }
        for row in libur_rows
    ]

def generator_jadwal(
        weekly_rows: List[JadwalTersedia],
        libur_rows: List[JadwalLibur],
        start_date: date,
        days = 7
) -> list[dict]:
    now = datetime.now(ZoneInfo("Asia/Jakarta"))

    weekly_by_day = {}
    for row in weekly_rows:
        day_key = str(row["day_of_week"]).strip().lower()
        weekly_by_day.setdefault(day_key, []).append(row)

    for rows in weekly_by_day.values():
        rows.sort(key=lambda item: item["start_time"])
    
    libur_map = {}
    for libur in libur_rows:
        jadwal_tersedia_id = libur["jadwal_tersedia_id"]
        tanggal = libur["tanggal"]
        libur_map.setdefault(jadwal_tersedia_id, set()).add(tanggal)
    
    result = {}

    for i in range(days):
        base_date = start_date + timedelta(days=i)
        hari_ini = mapping_hari(base_date.weekday())
        daily_rows = weekly_by_day.get(hari_ini, [])

        for jadwal in daily_rows:
            current_date = base_date
            if current_date == now.date() and jadwal["start_time"] <= now.time():
                current_date = current_date + timedelta(days=7)

            is_libur = current_date in libur_map.get(jadwal["id"], set())

            item = {
                "id": jadwal["id"],
                "tanggal": current_date,
                "day_of_week": hari_ini,
                "konselor_id": jadwal["konselor_id"],
                "konselor_nama": jadwal["konselor_nama"],
                "start_time": jadwal["start_time"],
                "end_time": jadwal["end_time"],
                "status": "tutup" if is_libur else "buka",
            }

            result.setdefault(hari_ini, []).append(item)
    return result

def get_jadwal_tersedia_service(
    db: Optional[Session] = None,
):
    start_date = datetime.now(ZoneInfo("Asia/Jakarta")).date()
    end_date = start_date + timedelta(days=14)

    weekly_rows = get_jadwal_tersedia_weekly(db)
    libur_rows = get_libur(db, start_date, end_date)
    jadwal = generator_jadwal(weekly_rows, libur_rows, start_date)
    return jadwal

def post_jadwal_tersedia_service(
    db: Optional[Session] = None,
    jadwal_data: JadwalTersediaCreate = None
):
    Session = db or SessionLocal()

    try:
        _ensure_no_overlapping_schedule(
            Session,
            jadwal_data.konselor_id,
            jadwal_data.day_of_week,
            jadwal_data.start_time,
            jadwal_data.end_time,
        )

        new_jadwal = JadwalTersedia(
            konselor_id=jadwal_data.konselor_id,
            day_of_week=jadwal_data.day_of_week,
            start_time=jadwal_data.start_time,
            end_time=jadwal_data.end_time,
        )

        Session.add(new_jadwal)
        Session.commit()
        Session.refresh(new_jadwal)

        return {
            "id": new_jadwal.id,
            "konselor_id": new_jadwal.konselor_id,
            "day_of_week": new_jadwal.day_of_week,
            "start_time": new_jadwal.start_time,
            "end_time": new_jadwal.end_time,
        }
    except HTTPException:
        Session.rollback()
        raise
    except Exception as e:
        Session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Gagal membuat jadwal: {str(e)}"
        )
    finally:
        if db is None:
            Session.close()

def _get_jadwal_tersedia_orm(
        Session: Session,
        jadwal_tersedia_id: int,
) -> JadwalTersedia:
    jadwal_tersedia = (
        Session.query(JadwalTersedia)
        .filter(
            JadwalTersedia.id == jadwal_tersedia_id,
            JadwalTersedia.deleted_at.is_(None),
        )
        .first()
    )
    if not jadwal_tersedia:
        raise HTTPException(status_code=404, detail="Jadwal Tersedia not found")
    return jadwal_tersedia

def _ensure_no_overlapping_schedule(
        Session: Session,
        konselor_id: int,
        day_of_week: str,
        start_time,
        end_time,
        exclude_id: int | None = None,
) -> None:
    query = Session.query(JadwalTersedia).filter(
        JadwalTersedia.deleted_at.is_(None),
        JadwalTersedia.konselor_id == konselor_id,
        JadwalTersedia.day_of_week == day_of_week,
        JadwalTersedia.start_time < end_time,
        JadwalTersedia.end_time > start_time,
    )

    if exclude_id is not None:
        query = query.filter(JadwalTersedia.id != exclude_id)

    existing = query.first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Jadwal bentrok dengan {existing.day_of_week} "
                f"{existing.start_time.strftime('%H:%M')} - {existing.end_time.strftime('%H:%M')}"
            )
        )

def get_jadwal_tersedia_by_id_service(
        db: Optional[Session] =None,
        jadwal_tersedia_id: int = None
):
    Session = db or SessionLocal()
    jadwal_tersedia = _get_jadwal_tersedia_orm(Session, jadwal_tersedia_id)

    return {
        "id": jadwal_tersedia.id,
        "konselor_id": jadwal_tersedia.konselor_id,
        "day_of_week": jadwal_tersedia.day_of_week,
        "start_time": jadwal_tersedia.start_time,
        "end_time": jadwal_tersedia.end_time,
    }


def edit_jadwal_tersedia_service(
        db:Optional[Session] = None,
        jadwal_tersedia_id: int = None,
        new_jadwal_data: JadwalTersediaUpdate = None
):
    Session = db or SessionLocal()
    jadwal_tersedia = _get_jadwal_tersedia_orm(Session, jadwal_tersedia_id)

    
    update_data = new_jadwal_data.model_dump(exclude_unset=True)
    next_day = update_data.get("day_of_week", jadwal_tersedia.day_of_week)
    next_start = update_data.get("start_time", jadwal_tersedia.start_time)
    next_end = update_data.get("end_time", jadwal_tersedia.end_time)

    _ensure_no_overlapping_schedule(
        Session,
        jadwal_tersedia.konselor_id,
        next_day,
        next_start,
        next_end,
        exclude_id=jadwal_tersedia.id,
    )

    for field, value in update_data.items():
        setattr(jadwal_tersedia, field, value)

    Session.commit()
    Session.refresh(jadwal_tersedia)
    
    return {
        "id": jadwal_tersedia.id,
        "konselor_id": jadwal_tersedia.konselor_id,
        "day_of_week": jadwal_tersedia.day_of_week,
        "start_time": jadwal_tersedia.start_time,
        "end_time": jadwal_tersedia.end_time,
    }

def delete_jadwal_tersedia_service(
        db:Optional[Session]=None,
        jadwal_tersedia_id: int = None
):
    Session = db or SessionLocal()
    jadwal = _get_jadwal_tersedia_orm(Session, jadwal_tersedia_id)
    jadwal.deleted_at = date.today()
    Session.commit()
    return {
        "id": jadwal.id,
        "konselor_id": jadwal.konselor_id,
        "day_of_week": jadwal.day_of_week,
        "start_time": jadwal.start_time,
        "end_time": jadwal.end_time,
        "deleted_at": jadwal.deleted_at,
    }

