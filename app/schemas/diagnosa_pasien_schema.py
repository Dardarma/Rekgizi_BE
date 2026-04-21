import datetime
from typing import Optional
from pydantic import BaseModel

class diagnosaPasienBasic(BaseModel):
    id: int
    id_diagnosa: int 
    id_rekam_pasien: int
    
class DiagnosaItem(BaseModel):
    id: Optional[int] = None   
    id_diagnosa: int 
    
class diagnosaRequest(BaseModel):
    data: list[DiagnosaItem]
    
class APIResponseDiagnosaPasien(BaseModel):
    status_code: int
    message : str
    data : list[diagnosaPasienBasic]


    