from sqlalchemy.orm import Session, joinedload, with_loader_criteria
from app.models import Parameter, ParameterCalculation, ParameterCalculationSource
from app.schemas.parameter_schema import parameterCreate, parameterUpdate
from sqlalchemy import func
from fastapi import HTTPException
from app.service.master.parameter_calculation_service import sync_parameter_calculation

def get_parameter_service(
    db: Session,
):
    parameter = (
        db.query(Parameter)
        .options(joinedload(Parameter.calculation).joinedload(ParameterCalculation.sources))
        .options(
            with_loader_criteria(ParameterCalculation, ParameterCalculation.deleted_at.is_(None)),
            with_loader_criteria(ParameterCalculationSource, ParameterCalculationSource.deleted_at.is_(None)),
        )
        .filter(Parameter.deleted_at.is_(None))
        .all()
    )

    return parameter

def get_parameter_by_id_service(
    db: Session,
    parameter_id: int,
):
    parameter = db.query(Parameter)\
    .options(joinedload(Parameter.calculation).joinedload(ParameterCalculation.sources))\
    .options(
        with_loader_criteria(ParameterCalculation, ParameterCalculation.deleted_at.is_(None)),
        with_loader_criteria(ParameterCalculationSource, ParameterCalculationSource.deleted_at.is_(None)),
    )\
    .filter(Parameter.id == parameter_id
    ).filter(Parameter.deleted_at.is_(None)
    ).first()
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    return parameter

def create_parameter_service(
    db: Session,
    payload: parameterCreate
):
    new_parameter = Parameter(
        nama=payload.nama,
        kategori=payload.kategori,
        tipe_input=payload.tipe_input,
        important=payload.important,
        satuan = payload.satuan
    )

    db.add(new_parameter)
    db.flush()
    sync_parameter_calculation(db, new_parameter.id, payload.calculation)
    db.commit()
    db.refresh(new_parameter)

    return new_parameter

def updated_parameter_service(
    db: Session,
    parameter_id: int,
    payload: parameterUpdate
):
    parameter = db.query(Parameter).filter(Parameter.id == parameter_id).filter(Parameter.deleted_at.is_(None)).first()
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    
    if payload.nama is not None:
        parameter.nama = payload.nama
    if payload.kategori is not None:
        parameter.kategori = payload.kategori
    if payload.tipe_input is not None:
        parameter.tipe_input = payload.tipe_input
    if payload.satuan is not None:
        parameter.satuan = payload.satuan
    if payload.important is not None:
        parameter.important = payload.important

    if "calculation" in payload.model_fields_set:
        sync_parameter_calculation(db, parameter.id, payload.calculation)

    db.commit()
    db.refresh(parameter)

    return parameter

def delete_parameter_service(
    db: Session,
    parameter_id: int,
):
    parameter = db.query(Parameter).filter(Parameter.id == parameter_id).first()
    
    parameter.deleted_at = func.now()
    sync_parameter_calculation(db, parameter.id, None)
    db.commit()

    return parameter
