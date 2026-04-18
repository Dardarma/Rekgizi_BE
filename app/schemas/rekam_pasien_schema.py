from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RekamPasienBase(BaseModel):
    id : int
    pasien_id : int
    nama_pasien : str
    tanggal_assesmen : datetime
    status : str
    intervensi_id : Optional[int] = None
    tujuan_intervensi : Optional[str] = None
    prinsip_intervensi : Optional[str] = None
    edukasi_intervensi : Optional[str] = None
    rencana_diet_intervensi : Optional[str] = None

class RekamPasienCreate(BaseModel):
    pasien_id : int
    tanggal_assesmen : datetime
    status : str
    intervensi_id : Optional[int] = None
    tujuan_intervensi : Optional[str] = None
    prinsip_intervensi : Optional[str] = None
    edukasi_intervensi : Optional[str] = None
    rencana_diet_intervensi : Optional[str] = None

class RekamPasienUpdate(BaseModel):
    pasien_id : Optional[int] = None
    tanggal_assesmen : Optional[datetime] = None
    status : Optional[str] = None
    intervensi_id : Optional[int] = None
    tujuan_intervensi : Optional[str] = None
    prinsip_intervensi : Optional[str] = None
    edukasi_intervensi : Optional[str] = None
    rencana_diet_intervensi : Optional[str] = None

