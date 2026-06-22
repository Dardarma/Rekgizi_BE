from datetime import date
from pydantic import BaseModel
from typing import Optional


class dashboardAhliGiziBaseInfo(BaseModel):
    tahun: int
    bulan: int
    total_case: int
    total_approved: int
    total_appoinment: int
    total_article: int

class rekamPaseinDashboard(BaseModel):
    id:int
    nama: str
    status: str
    tanggal_asesmen:str


