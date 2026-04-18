from datetime import date
from typing import Optional
from pydantic import BaseModel, model_validator, EmailStr

from app.models.users import RoleEnum, KelaminEnum
from app.schemas.meta_schema import PaginateSchema

class Alamat(BaseModel):
    desa: Optional[str] = None
    kecamatan: Optional[str] = None
    kota: Optional[str] = None
    provinsi: Optional[str] = None
    lengkap: Optional[str] = None


class PasswordConfirmationMixin(BaseModel):
    password: str
    password_validation: str

    @model_validator(mode="after")
    def validate_password(self):
        if self.password != self.password_validation:
            raise ValueError("password tidak sama")
        return self


class OptionalPasswordConfirmationMixin(BaseModel):
    password: Optional[str] = None
    password_validation: Optional[str] = None

    @model_validator(mode="after")
    def validate_password(self):
        if self.password or self.password_validation:
            if self.password != self.password_validation:
                raise ValueError("password tidak sama")
        return self


class UserBase(PasswordConfirmationMixin):
    nama: str
    jenis_kelamin: KelaminEnum
    alamat: Alamat
    email: EmailStr
    tanggal_lahir: date


class UserBasicInfo(BaseModel):
    id : int
    role: Optional[RoleEnum] = None
    nama: Optional[str] = None
    jenis_kelamin: Optional[KelaminEnum] = None
    alamat: Optional[Alamat] = None
    email: Optional[EmailStr] = None
    tanggal_lahir: Optional[date] = None
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    role: RoleEnum


class UserRegister(UserBase):
    pass

class UserUpdate(OptionalPasswordConfirmationMixin):
    role: Optional[RoleEnum] = None
    nama: Optional[str] = None
    jenis_kelamin: Optional[KelaminEnum] = None
    alamat: Optional[Alamat] = None
    email: Optional[EmailStr] = None
    tanggal_lahir: Optional[date] = None

class userResponseAPI(BaseModel):
    meta: PaginateSchema
    data: list[UserBasicInfo]
    
class UserSearchRequest(BaseModel):
    search: str = ""
    current_page: int = 1
    limit: int = 10

    
    