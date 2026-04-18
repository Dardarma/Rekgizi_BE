from pydantic import BaseModel
from datetime import date
from app.schemas.meta_schema import PaginateSchema

class JadwalLiburBasicInfo(BaseModel):
    id: int
    jadwal_tersedia: int
    tanggal: date
    end_time: str
    start_time: str
    day_of_week: str

class JadwalLiburCreate(BaseModel):
    jadwal_tersedisa_id: int
    tanggal: date

class JadwalLiburDeleted(BaseModel):
    id: int
    jadwal_tersedia: int
    tanggal: date
    end_time: str
    start_time: str
    day_of_week: str
    deleted_at: str | None = None