from sqlalchemy import TIMESTAMP, Column, Integer, String, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    judul = Column(String(255))
    konten = Column(Text)
    thumbnail_url = Column(String(255))
    is_published = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    pembuat = relationship("User", back_populates="articles")
