import datetime
from typing import Optional
from pydantic import BaseModel

class diagnosaPasienBasic(BaseModel):
    id: int
    diagnosa_id: int
    rekam_pasien_id: int
    
class DiagnosaItem(BaseModel):
    id: Optional[int] = None   
    diagnosa_id: int 
    
class diagnosaRequest(BaseModel):
    rekam_pasien_id: int
    data: list[DiagnosaItem]
    