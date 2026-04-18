import datetime
from typing import Optional
from pydantic import BaseModel

class IntervensiBasicInfo(BaseModel):
    jenis_diet : str
    tujuan : str
    prinsip : str
    edukasi : str
    protein : int
    energi : int
    karbohidrat : int
class IntervensiInfo(IntervensiBasicInfo):
    id : int

class IntervensEdit(BaseModel):
    id : Optional[str]
    jenis_diet : Optional[str]
    tujuan : Optional[str]
    prinsip : Optional[str]
    edukasi : Optional[str]
    protein : Optional[int]
    energi : Optional[int]
    karbohidrat : Optional[int]

class IntervensiDeleted(IntervensiInfo):
    deleted_at: Optional[datetime.datetime] = None
        
class APIResponseIntervensi(BaseModel):
    status_code: int
    message: str
    data: list[IntervensiInfo]

class APIResponseIntervensiId(BaseModel):
    status_code: int
    message: str
    data: IntervensiInfo
    
class APIResponseIntervensiDeleted(BaseModel):
    status_code: int
    message: str
    data: IntervensiDeleted



