from http.client import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import OpsiParameter, Parameter
from app.schemas.parameter_opsi_schema import OpsiParameterCreate, OpsiParameterUpdate
from sqlalchemy.exc import IntegrityError

def get_opsi_parameter_by_param_service(
    db: Session,
    parameter_id: int,
):
    opsi_parameter = db.query(OpsiParameter
    ).filter(OpsiParameter.parameter_id == parameter_id
    ).filter(OpsiParameter.deleted_at == None).all()

    if not opsi_parameter:
        raise HTTPException(status_code=404, detail="Opsi Parameter not found")
    
    return opsi_parameter

def get_opsi_parameter_by_id_service(
    db: Session,
    opsi_parameter_id: int,
):
    opsi_parameter = db.query(OpsiParameter
    ).filter(OpsiParameter.id == opsi_parameter_id
    ).filter(OpsiParameter.deleted_at == None).first()

    if not opsi_parameter:
        raise HTTPException(status_code=404, detail="Opsi Parameter not found")
    
    return opsi_parameter

def post_opsi_parameter_service(
    db: Session,
    payload: OpsiParameterCreate,
):
    parameter = db.query(Parameter
    ).filter(Parameter.id == payload.parameter_id
    ).filter(Parameter.deleted_at == None
    ).first()

    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    
    exist = db.query(OpsiParameter
    ).filter(OpsiParameter.jawaban == payload.jawaban
    ).filter(OpsiParameter.deleted_at == None
    ).filter(OpsiParameter.parameter_id == payload.parameter_id
    ).first()

    if exist:
        raise HTTPException(status_code=400, detail="Opsi Parameter already exists")

    try:
        new_opsi_parameter = OpsiParameter(
            parameter_id=payload.parameter_id,
            jawaban=payload.jawaban,
        )
        db.add(new_opsi_parameter)
        db.commit()
        db.refresh(new_opsi_parameter)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Opsi Parameter already exists or invalid reference"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    return new_opsi_parameter

def updated_opsi_parameter_service(
    db: Session,
    id: int,
    payload: OpsiParameterUpdate,
):
    opsi_paramater = db.query(OpsiParameter
        ).filter(OpsiParameter.id == id
        ).filter(OpsiParameter.deleted_at == None
        ).first()
   
    if not opsi_paramater:
        raise HTTPException(status_code=404, detail="Opsi Parameter not found")
    
    opsi_paramater.jawaban = payload.jawaban

    exist = (
        db.query(OpsiParameter)
        .filter(OpsiParameter.jawaban == payload.jawaban)
        .filter(OpsiParameter.deleted_at == None)
        .filter(OpsiParameter.parameter_id == opsi_paramater.parameter_id)
        .filter(OpsiParameter.id != id)
        .first()
    )
    if exist:
        raise HTTPException(status_code=400, detail="Opsi Parameter already exists")
    
    db.commit()
    db.refresh(opsi_paramater)

    return opsi_paramater

def delete_opsi_parameter_service(
    db: Session,
    opsi_parameter_id: int,
):
    opsi_parameter = db.query(OpsiParameter
    ).filter(OpsiParameter.id == opsi_parameter_id
    ).filter(OpsiParameter.deleted_at == None).first()

    if not opsi_parameter:
        raise HTTPException(status_code=404, detail="Opsi Parameter not found")
    
    opsi_parameter.deleted_at = func.now()
    db.commit()
    db.refresh(opsi_parameter)

    return opsi_parameter
