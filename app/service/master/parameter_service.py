from sqlalchemy.orm import Session
from app.models import Parameter
from app.schemas.parameter_schema import parameterCreate, parameterUpdate
from sqlalchemy import func
from fastapi import HTTPException

def get_parameter_service(
    db: Session,
):
    parameter = (
        db.query(Parameter)
        .filter(Parameter.deleted_at.is_(None))
        .all()
    )

    return parameter

def get_parameter_by_id_service(
    db: Session,
    parameter_id: int,
):
    parameter = db.query(Parameter)\
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
    
    parameter.nama = payload.nama
    parameter.kategori = payload.kategori
    parameter.tipe_input = payload.tipe_input
    parameter.satuan = payload.satuan
    parameter.important = payload.important

    db.commit()
    db.refresh(parameter)

    return parameter

def delete_parameter_service(
    db: Session,
    parameter_id: int,
):
    parameter = db.query(Parameter).filter(Parameter.id == parameter_id).first()
    
    parameter.deleted_at = func.now()
    db.commit()

    return parameter