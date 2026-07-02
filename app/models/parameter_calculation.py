from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ParameterCalculation(Base):
    __tablename__ = "parameter_calculation"

    id = Column(Integer, primary_key=True, index=True)
    target_parameter_id = Column(Integer, ForeignKey("parameter.id"), nullable=False, unique=True)
    formula = Column(Text, nullable=False)
    rounding = Column(Integer, nullable=True, default=2)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    target_parameter = relationship("Parameter", back_populates="calculation")
    sources = relationship(
        "ParameterCalculationSource",
        back_populates="calculation",
        cascade="all, delete-orphan",
    )


class ParameterCalculationSource(Base):
    __tablename__ = "parameter_calculation_source"

    id = Column(Integer, primary_key=True, index=True)
    calculation_id = Column(Integer, ForeignKey("parameter_calculation.id"), nullable=False)
    source_parameter_id = Column(Integer, ForeignKey("parameter.id"), nullable=False)
    variable_name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    calculation = relationship("ParameterCalculation", back_populates="sources")
    source_parameter = relationship("Parameter", foreign_keys=[source_parameter_id])
