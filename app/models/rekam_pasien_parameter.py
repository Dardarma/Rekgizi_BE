from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class RekamPasienParameter(Base):
    __tablename__ = "rekam_pasien_parameter"
    id = Column(Integer, primary_key=True)
    rekam_pasien_id = Column(Integer, ForeignKey('rekam_pasien.id'))
    parameter_id = Column(Integer, ForeignKey('parameter.id'))
    opsi_parameter_id = Column(Integer, ForeignKey('opsi_parameter.id'))
    jawaban = Column(Text)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    rekam_pasien = relationship(
        'RekamPasien',
        back_populates= 'rekam_pasien_parameter'
    )

    parameter = relationship(
        'Parameter',
        back_populates='rekam_pasien_parameter'
    )

    opsi_parameter = relationship(
        'OpsiParameter',
        back_populates='rekam_pasien_parameter'
    )

