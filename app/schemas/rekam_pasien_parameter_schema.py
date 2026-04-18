from pydantic import BaseModel
from typing import List, Optional

class rekamPasienParameterBase(BaseModel):
    parameter_id:int
    jawaban: Optional[str] = None
    opsi_parameter_id: Optional[int] = None

class rekamPasienParameterRequest(BaseModel):
    rekam_pasien_id:int
    data: List[rekamPasienParameterBase]
    
class rekamPasienParameterInfo(rekamPasienParameterBase):
    id:int
    
class rekamPasienParmeterResponse(BaseModel):
    status_code: int
    message: str
    data: list[rekamPasienParameterBase]