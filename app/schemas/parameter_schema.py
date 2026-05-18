from pydantic import BaseModel, Field
from typing import Optional, List

from app.models.parameter import TipeInputEnum
from app.schemas.parameter_opsi_schema import OpsiParameterBaseInfo

class parameterBaseInfo(BaseModel):
    id: int
    nama: str
    kategori: str
    tipe_input: TipeInputEnum
    satuan: Optional[str]
    important: bool
    
    model_config = {
        "from_attributes": True
    }

class parameterCreate(BaseModel):
    nama: str
    kategori: str
    tipe_input: TipeInputEnum
    satuan : str
    important: bool

class parameterUpdate(BaseModel):
    nama: Optional[str] = None
    kategori: Optional[str] = None
    tipe_input: Optional[TipeInputEnum] = None
    satuan: Optional[str]
    important: Optional[bool] = None
    
from typing import List, Optional

class ParameterWithOpsi(parameterBaseInfo):
    opsi: Optional[List[OpsiParameterBaseInfo]] = Field(default=[], alias="opsi_parameter")
    
class APIResponsPamarematerInput(BaseModel):
    status_code: int
    message: str
    data: List[ParameterWithOpsi]
    
    model_config = {
        "from_attributes": True
    }
