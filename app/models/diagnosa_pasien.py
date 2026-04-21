from sqlalchemy import Integer, Column, ForeignKey, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.core.database import Base

UniqueConstraint('rekam_pasien_id', 'diagnosa_id', 'deleted_at')

class DiagnosaPasien(Base):
    __tablename__ = "diagnosa_pasien"

    id = Column(Integer, primary_key=True, index=True)
    id_rekam_pasien = Column(Integer, ForeignKey('rekam_pasien.id'), nullable=False)
    id_diagnosa = Column(Integer, ForeignKey('diagnosa.id'), nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    rekam_pasien = relationship('RekamPasien', back_populates='diagnosa_pasien')
    diagnosa = relationship('Diagnosa', back_populates='diagnosa_pasien')