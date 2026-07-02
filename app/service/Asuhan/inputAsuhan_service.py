from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.models import Parameter, RekamPasienParameter
from app.models.diagnosa_pasien import DiagnosaPasien
from app.models.opsi_parameter import OpsiParameter
from app.models.parameter_calculation import ParameterCalculation, ParameterCalculationSource
from app.service.master.parameter_calculation_service import calculate_rekam_pasien_parameters
import numpy as np

def get_parameter_input_service(
    db:Session
):
    from sqlalchemy.orm import joinedload, with_loader_criteria

    query = (
        db.query(Parameter)
        .options(
            joinedload(Parameter.opsi_parameter),
            joinedload(Parameter.calculation).joinedload(ParameterCalculation.sources),
            with_loader_criteria(
                OpsiParameter,
                OpsiParameter.deleted_at.is_(None)
            ),
            with_loader_criteria(
                ParameterCalculation,
                ParameterCalculation.deleted_at.is_(None)
            ),
            with_loader_criteria(
                ParameterCalculationSource,
                ParameterCalculationSource.deleted_at.is_(None)
            )
        )
        .filter(Parameter.deleted_at.is_(None)).all()
    )
    
    if not query:
        raise HTTPException(status_code=404, detail="Intervensi not found")
    
    return query

def saveParameterPasien(
    db: Session,
    rekam_pasien_id: int,
    items
):
    for item in items:
        existing = db.query(RekamPasienParameter).filter(
            RekamPasienParameter.rekam_pasien_id == rekam_pasien_id,
            RekamPasienParameter.parameter_id == item.parameter_id,
            RekamPasienParameter.deleted_at.is_(None)
        ).first()

        empty = (
            (item.jawaban is None or str(item.jawaban).strip() == "")
            and item.opsi_parameter_id is None
        )

        if empty:
            if existing:
                existing.deleted_at = func.now()
            continue

        if existing:
            existing.jawaban = item.jawaban
            existing.opsi_parameter_id = item.opsi_parameter_id
        else:
            db.add(RekamPasienParameter(
                rekam_pasien_id=rekam_pasien_id,
                parameter_id=item.parameter_id,
                jawaban=item.jawaban,
                opsi_parameter_id=item.opsi_parameter_id
            ))

    calculate_rekam_pasien_parameters(db, rekam_pasien_id)
    db.commit()
    return items


def getRekamPasienParameterService(
    db:Session,
    rekam_pasien_id: int,
):
    query = (
        db.query(RekamPasienParameter)
        .options(joinedload(RekamPasienParameter.opsi_parameter))
        .filter(
            RekamPasienParameter.rekam_pasien_id == rekam_pasien_id,
            RekamPasienParameter.deleted_at.is_(None)
        )
        .all()
    )
    
    if not query:
        raise HTTPException(status_code=404, detail="Parameter jawaban not found")
    
    return query


def saveDiagnosaPasienService(
    db: Session,
    rekam_pasien_id: int,
    items
):
    existing = db.query(DiagnosaPasien).filter(
        DiagnosaPasien.id_rekam_pasien == rekam_pasien_id,
        DiagnosaPasien.deleted_at.is_(None)
    ).all()
    
    existing_map = {d.id: d for d in existing}
    
    incoming_ids = {
        item.id for item in items
        if getattr(item, "id", None) is not None
    }
    
    for d in existing:
        if d.id not in incoming_ids:
            d.deleted_at = func.now()
            

    for item in items:
        if item.id is not None:
            if item.id in existing_map:
                diagnosa = existing_map[item.id]
                diagnosa.diagnosa_id = item.id_diagnosa
            else:
                continue
        else:
            db.add(DiagnosaPasien(
                id_rekam_pasien=rekam_pasien_id,
                id_diagnosa=item.id_diagnosa
            ))
    
    db.commit()
    
    result = (
    db.query(DiagnosaPasien)
        .filter(
            DiagnosaPasien.id_rekam_pasien == rekam_pasien_id,
            DiagnosaPasien.deleted_at.is_(None)
        )
        .all()
    )

    return result

def getDiagnosaPasienService(
    db: Session,
    rekam_pasien_id: int
):
    query = (
        db.query(DiagnosaPasien)
        .filter(
            DiagnosaPasien.id_rekam_pasien == rekam_pasien_id,
            DiagnosaPasien.deleted_at.is_(None)
        )
        .all()
    )
    
    if not query:
        raise HTTPException(status_code=404, detail="Diagnosa pasien not found")

    return query

