from sqlalchemy import Column, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Intervensi(Base):
    __tablename__ = 'intervensi'

    id = Column(Integer, primary_key=True, index=True)
    jenis_diet = Column(Text)
    tujuan = Column(Text)
    prinsip = Column(Text)
    edukasi = Column(Text)
    protein = Column(Integer)
    energi = Column(Integer)
    karbohidrat = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)
    rekam_pasien = relationship("RekamPasien", back_populates="intervensi")