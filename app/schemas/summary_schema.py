from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ParameterSummaryItem(BaseModel):
    nama_parameter: str
    kategori: Optional[str]
    jawaban: Optional[str]
    
class DiagnosaSummaryItem(BaseModel):
    kode: str
    diagnosa: str

class RekamPasienSummary(BaseModel):
    nama: str
    jenis_kelamin: str
    alamat: dict
    usia: int
    tanggal_asesmen: datetime
    status: str
    tujuan_intervensi: Optional[str]
    prinsip_intervensi: Optional[str]
    edukasi_intervensi: Optional[str]
    jenis_diet: Optional[str]
    protein: Optional[int]
    energi: Optional[int]
    karbohidrat: Optional[int]
    parameter: List[ParameterSummaryItem]
    diagnosa: List[DiagnosaSummaryItem]

class RekamPasienSummaryResponse(BaseModel):
    status_code: int
    message : str
    data: RekamPasienSummary