from sqlalchemy import  TIMESTAMP,  CheckConstraint, ForeignKey, Integer, String, Time, Column, func
from sqlalchemy.orm import relationship

from app.core.database import Base

class JadwalTersedia(Base):
    __tablename__ = 'jadwal_tersedia'

    __table_args__ = (
        CheckConstraint(
            "day_of_week In ('Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu')",
            name="chk_jadwal_tersedia_day_of_week",
        ),
    )

    id = Column(Integer, primary_key= True, index=True)
    konselor_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    day_of_week = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    konselor = relationship("User", foreign_keys=[konselor_id], back_populates="jadwal_tersedia")

    jadwal_libur = relationship("JadwalLibur", back_populates="jadwal_tersedia")

