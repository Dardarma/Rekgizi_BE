from sqlalchemy import TIMESTAMP, Column, Integer, ForeignKey, Text, func, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum


from app.core.database import Base

class statusEnum(PyEnum):
    belum_ditinjau = 'belum_ditinjau'
    ditinjau ='ditinjau'
    disetujui = 'disetujui'

class RekamPasien(Base):
    __tablename__ = 'rekam_pasien'

    id = Column(Integer, primary_key=True, index=True)
    pasien_id = Column(Integer, ForeignKey('users.id'))
    tanggal_asesmen = Column(TIMESTAMP, nullable=False)
    status = Column(Enum(statusEnum, name="enum_status"), nullable=False)
    intervensi_id = Column(Integer, ForeignKey('intervensi.id'))
    tujuan_intervensi = Column(Text, nullable=True)
    jenis_diet = Column(Text, nullable=True)
    prinsip_intervensi = Column(Text, nullable=True)
    edukasi_intervensi = Column(Text, nullable=True)
    protein = Column(Integer, nullable=True)
    energi = Column(Integer, nullable=True)
    karbohidrat = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    pasien = relationship("User", back_populates="rekam_pasien")
    intervensi = relationship("Intervensi", back_populates="rekam_pasien")
    rekam_pasien_parameter = relationship(
        "RekamPasienParameter", back_populates="rekam_pasien", cascade="all, delete-orphan"
    )
    diagnosa_pasien = relationship(
        "DiagnosaPasien", back_populates="rekam_pasien", cascade="all, delete-orphan"
    )


