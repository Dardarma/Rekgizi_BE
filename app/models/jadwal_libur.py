from sqlalchemy import TIMESTAMP, Column, Date, ForeignKey, Integer, Time, func
from sqlalchemy.orm import relationship

from app.core.database import Base

class JadwalLibur(Base):
    __tablename__ = 'jadwal_libur'

    id = Column(Integer, primary_key=True, index=True)
    jadwal_tersedia_id = Column(Integer, ForeignKey('jadwal_tersedia.id'), nullable=False)
    tanggal = Column(Date, nullable=False) 

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    jadwal_tersedia = relationship("JadwalTersedia", foreign_keys=[jadwal_tersedia_id], back_populates="jadwal_libur")
    