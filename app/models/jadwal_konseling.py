from sqlalchemy import TIMESTAMP, Column, Integer, String, Text, ForeignKey, DATE, func
from sqlalchemy.orm import relationship

from app.core.database import Base

class JadwalKonseling(Base):
    __tablename__ = 'jadwal_konseling'

    id = Column(Integer, primary_key=True, index=True)
    pasien_id = Column(Integer, ForeignKey('users.id'))
    konselor_id = Column(Integer, ForeignKey('users.id'))
    jadwal_tersedia_id = Column(Integer, ForeignKey('jadwal_tersedia.id'), nullable=False)
    tanggal_konseling = Column(DATE)
    status = Column(String, nullable=False, default='pending')
    catatan = Column(Text)
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)
    pasien = relationship("User", foreign_keys=[pasien_id], back_populates="jadwal_konseling")
    konselor = relationship("User", foreign_keys=[konselor_id], back_populates="jadwal_konseling_konselor")
