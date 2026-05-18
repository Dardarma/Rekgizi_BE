from typing import Dict,Optional
from pydantic import BaseModel, model_validator
from datetime import date, time, datetime, timedelta
from fastapi import HTTPException

class JadwalTersediaInfo(BaseModel):
    id: int
    tanggal: date
    day_of_week:str
    konselor_id: int
    konselor_nama: str
    start_time: time
    end_time: time
    status: str

class JadwalTersediaListInfo(BaseModel):
    jadwal_tersedia: Dict[str,list[JadwalTersediaInfo]]

class JadwalTersediaValidation(BaseModel):
    start_time: time | None = None
    end_time: time | None = None

    @model_validator(mode="after")
    def validate_time(self):
        if self.start_time is None or self.end_time is None:
            return self
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(date.today(), self.end_time)

        if start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="start_time harus sebelum end_time")

        if end_dt - start_dt < timedelta(minutes=30):
            raise HTTPException(status_code=400, detail="Jadwal minimal berdurasi 30 menit")
        
        return self
    
class jadwalTersediaBasicInfo(BaseModel):
    id: int
    konselor_id: int
    day_of_week: str
    start_time: time
    end_time: time
    

class JadwalTersediaCreate(JadwalTersediaValidation):
    konselor_id: int
    day_of_week: str
    start_time: time
    end_time: time



class JadwalTersediaUpdate(JadwalTersediaValidation):
    day_of_week: Optional[str] | None = None
    start_time: Optional[time] | None = None
    end_time: Optional[time] | None = None




