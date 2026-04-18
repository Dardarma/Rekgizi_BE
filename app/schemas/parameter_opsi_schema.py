from pydantic import BaseModel
from typing import Optional, List

class OpsiParameterBaseInfo(BaseModel):
    id: int
    parameter_id: int
    jawaban: str
    
    model_config = {
        "from_attributes": True
    }


class OpsiParameterCreate(BaseModel):
    parameter_id: int
    jawaban: str


class OpsiParameterUpdate(BaseModel):
    parameter_id: Optional[int]
    jawaban: Optional[str] = None


class APIResponseOpsiParameter(BaseModel):
    status_code: int
    message: str
    data: List[OpsiParameterBaseInfo]


class APIResponseOpsiParameterID(BaseModel):
    status_code: int
    message: str
    data: OpsiParameterBaseInfo