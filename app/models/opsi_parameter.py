from sqlalchemy import TIMESTAMP, Column, Integer, Text, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base

class OpsiParameter(Base):
    __tablename__ = 'opsi_parameter'

    id = Column(Integer, primary_key=True, index=True)
    parameter_id = Column(Integer, ForeignKey('parameter.id'))
    jawaban = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(),  onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    parameter = relationship("Parameter", back_populates="opsi_parameter")
    rekam_pasien_parameter = relationship("RekamPasienParameter", back_populates="opsi_parameter")
 