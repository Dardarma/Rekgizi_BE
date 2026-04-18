from datetime import date, time
from typing import Optional
from pydantic import BaseModel

class jadwalKonselingBasicInfo(BaseModel):
    id: int
    pasien_id: int
    konselor_id: int
    nama_konselor: str
    nama_pasien: str
    jadwal_tersedia_id: int
    tanggal_konseling: date
    day_of_week: str
    start_time: time
    end_time: time
    status: str
    catatan: Optional[str] = None
    
class jadwalKonselingCreate(BaseModel):
    pasien_id: int
    konselor_id: int
    jadwal_tersedia_id: int
    tanggal_konseling: date
    status: str 
    catatan: Optional[str] = None

class jadwalKonselingUpdate(BaseModel):
    pasien_id: int | None = None
    konselor_id: int | None = None
    jadwal_tersedia_id: int | None = None
    tanggal_konseling: date | None = None

class JadwalKonselingStatus(BaseModel):
    status: str

class jadwalKonselingUbahCatatan(BaseModel):
    catatan: str | None = None