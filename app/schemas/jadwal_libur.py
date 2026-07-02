from pydantic import BaseModel
from datetime import date, time
from app.schemas.meta_schema import PaginateSchema

class JadwalLiburBasicInfo(BaseModel):
    id: int
    jadwal_tersedia: int
    tanggal: date
    end_time: str
    start_time: str
    day_of_week: str

class JadwalLiburCreate(BaseModel):
    jadwal_tersedia_id: int | None = None
    tanggal: date | None = None
    tanggal_mulai: date | None = None
    tanggal_selesai: date | None = None
    start_time: time | None = None
    end_time: time | None = None

class JadwalLiburDeleted(BaseModel):
    id: int
    jadwal_tersedia: int
    tanggal: date
    end_time: str
    start_time: str
    day_of_week: str
    deleted_at: str | None = None
