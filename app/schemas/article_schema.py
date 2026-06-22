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
    thumbnail_url: Optional[str] = None
    konten: Optional[str] = None
    is_published: bool = False

class articleUpdate(BaseModel):
    judul: Optional[str] = None
    konten: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_published: Optional[bool] = None

class articleAPIResponse(BaseModel):
    status_code: int
    message: str
    data: articleBaseInfo
