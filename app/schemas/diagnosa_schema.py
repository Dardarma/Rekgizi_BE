import datetime
from typing import Optional
from pydantic import BaseModel

class diagnosaBasicInfo(BaseModel):
    kode: str
    diagnosa: str

class diagnosaInfo(diagnosaBasicInfo):
    id: int
    
class diagnosaEdit(BaseModel):
    id : Optional[str]
    kode : Optional[str]
    diagnosa : Optional[str]

class diagnosaDelete(diagnosaInfo):
    deleted_at : Optional[datetime.datetime] = None
    
class APIResponsediagnosa(BaseModel):
    status_code : int
    message: str
    data: list[diagnosaInfo]
    
class APIResponsediagnosaId(BaseModel):
    status_code: int
    message : str
    data : diagnosaInfo
    
class APIResponseDeleted(BaseModel):
    status_code : int
    message: str
    data : diagnosaDelete
    
