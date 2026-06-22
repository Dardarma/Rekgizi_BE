from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class NotificationToken(Base):
    __tablename__ = "notification_tokens"
    __table_args__ = (
        UniqueConstraint("token", name="uq_notification_tokens_token"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, nullable=False)
    device_type = Column(String(50), nullable=True, default="web")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="notification_tokens")
