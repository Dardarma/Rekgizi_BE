from enum import Enum as PyEnum
from sqlalchemy import Column, Enum, Integer, String, Text, Date, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class RoleEnum(PyEnum):
    ahli_gizi = "ahli_gizi"
    pasien = "pasien"
    admin = "admin"
    tenaga_kesehatan = "tenaga_kesehatan"


class KelaminEnum(PyEnum):
    pria = "pria"
    wanita = "wanita"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    role = Column(Enum(RoleEnum, name="enum_role"), nullable=False)
    nama = Column(String(255), nullable=False)
    jenis_kelamin = Column(Enum(KelaminEnum, name="enum_gender"), nullable=False)
    alamat = Column(JSONB, nullable=False)
    tanggal_lahir = Column(Date, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    pass_hash = Column(String(255), nullable=True)
    reset_token = Column(Text, nullable=True)
    reset_token_expiry = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at = Column(TIMESTAMP, nullable=True)
    
    jadwal_konseling = relationship(
        "JadwalKonseling",
        foreign_keys="JadwalKonseling.pasien_id",
        back_populates="pasien"
    )

    jadwal_konseling_konselor = relationship(
        "JadwalKonseling",
        foreign_keys="JadwalKonseling.konselor_id",
        back_populates="konselor"
    )

    jadwal_tersedia = relationship(
        "JadwalTersedia",
        foreign_keys="JadwalTersedia.konselor_id",
        back_populates="konselor"
    )

    articles = relationship("Article", back_populates="pembuat")
    rekam_pasien = relationship("RekamPasien", back_populates="pasien")