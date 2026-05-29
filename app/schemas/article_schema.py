from datetime import date

from pydantic import BaseModel
from typing import Optional
from app.schemas.meta_schema import PaginateSchema

class articleBaseInfo(BaseModel):
    id: int
    user_id: int
    nama_pembuat: str
    judul: str
    thumbnail_url: Optional[str]
    konten: Optional[str]
    is_published: bool 
    tanggal:date

class articleGetResponse(BaseModel):
    data: list[articleBaseInfo]
    meta: PaginateSchema

class articleCreate(BaseModel):
    user_id: int
    judul: str
    thumbnail_url: Optional[str]
    konten: Optional[str]
    is_published: bool

class articleUpdate(BaseModel):
    judul: Optional[str]
    konten: Optional[str]
    thumbnail_url: Optional[str]
    is_published: Optional[bool]

class articleAPIResponse(BaseModel):
    status_code: int
    message: str
    data: articleBaseInfo
