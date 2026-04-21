from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RekamPasienBase(BaseModel):
    id : int
    pasien_id : int
    nama_pasien : Optional[str] = None
    tanggal_asesmen : datetime
    status : str
    intervensi_id : Optional[int] = None
    tujuan_intervensi : Optional[str] = None
    prinsip_intervensi : Optional[str] = None
    edukasi_intervensi : Optional[str] = None
    karbohidrat : Optional[int] = None
    protein : Optional[int] = None
    energi : Optional[int] = None


class RekamPasienCreate(BaseModel):
    pasien_id : int
    tanggal_assesmen : datetime
    status : str
    intervensi_id : Optional[int] = None
    tujuan_intervensi : Optional[str] = None
    prinsip_intervensi : Optional[str] = None
    edukasi_intervensi : Optional[str] = None
    karbohidrat : Optional[int] = None
    protein : Optional[int] = None
    energi : Optional[int] = None

class RekamPasienUpdate(BaseModel):
    pasien_id : Optional[int] = None
    tanggal_assesmen : Optional[datetime] = None
    status : Optional[str] = None
    intervensi_id : Optional[int] = None
    tujuan_intervensi : Optional[str] = None
    prinsip_intervensi : Optional[str] = None
    edukasi_intervensi : Optional[str] = None
    karbohidrat : Optional[int] = None
    protein : Optional[int] = None
    energi : Optional[int] = None
    
class IntervensiRekamPasienRequest(BaseModel):
    intervensi_id : int
    jenis_diet : str
    tujuan : str
    prinsip : str
    edukasi : str
    protein : int
    energi : int
    karbohidrat : int
    
class APIRekamPasien(BaseModel):
    status_code: int
    message: str
    data: RekamPasienBase

