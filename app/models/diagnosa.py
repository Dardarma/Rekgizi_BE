from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Diagnosa(Base):
    __tablename__ = "diagnosa"
    id = Column(Integer,primary_key=True)
    kode = Column(String)
    diagnosa = Column(String)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    diagnosa_pasien = relationship(
        'DiagnosaPasien',
        back_populates='diagnosa',
        cascade='all, delete-orphan'
    )
