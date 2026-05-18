from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Enum, Boolean
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.core.database import Base

class TipeInputEnum(PyEnum):
    text = 'text'
    number = 'number'
    boolean = 'boolean'
    select = 'select'
    textarea = 'textarea'
    date = 'date'
    
class Parameter(Base):
    __tablename__ = 'parameter'

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255))
    kategori = Column(String(50))
    tipe_input = Column(Enum(TipeInputEnum,name="enum_tipe_input"),nullable=False)
    important = Column(Boolean, default=False)
    satuan = Column(String)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    opsi_parameter = relationship(
        "OpsiParameter", back_populates="parameter", cascade="all, delete-orphan"
    )
    rekam_pasien_parameter = relationship(
        "RekamPasienParameter", back_populates="parameter", cascade="all, delete-orphan"
    )
