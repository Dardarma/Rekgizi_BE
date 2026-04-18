from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Intervensi
from app.schemas.intervensi_schema import IntervensiInfo

def get_intervensi_service(
    db: Session
):
    intervensi = db.query(Intervensi
    ).filter(Intervensi.deleted_at == None).all()

    if not intervensi:
        raise HTTPException(status_code=404, detail="Intervensi not found")
    
    return intervensi

def get_intervensi_by_id_service(
    db: Session,
    intervensi_id: int
):
    intervensi = db.query(Intervensi
    ).filter(Intervensi.id == intervensi_id
    ).filter(Intervensi.deleted_at == None).first()

    if not intervensi:
        raise HTTPException(status_code=404, detail="Intervensi not found")
    
    return intervensi


def create_intervensi_service(
    db: Session,
    intervensi_info: IntervensiInfo
):
    new_intervensi = Intervensi(
        jenis_diet = intervensi_info.jenis_diet,
        tujuan=intervensi_info.tujuan,
        prinsip=intervensi_info.prinsip,
        edukasi=intervensi_info.edukasi,
        protein = intervensi_info.protein,
        energi = intervensi_info.energi,
        karbohidrat = intervensi_info.karbohidrat
    )

    db.add(new_intervensi)
    db.commit()
    db.refresh(new_intervensi)

    return new_intervensi

def edit_intervensi_service(
    db: Session,
    intervensi_id: int,
    intervensi_info: IntervensiInfo
):
    intervensi = db.query(Intervensi
    ).filter(Intervensi.id == intervensi_id
    ).filter(Intervensi.deleted_at == None).first()

    if not intervensi:
        raise HTTPException(status_code=404, detail="Intervensi not found")
    
    intervensi.jenis_diet = intervensi_info.jenis_diet
    intervensi.tujuan = intervensi_info.tujuan
    intervensi.prinsip = intervensi_info.prinsip
    intervensi.edukasi = intervensi_info.edukasi
    intervensi.protein = intervensi_info.protein
    intervensi.karbohidrat = intervensi_info.karbohidrat
    intervensi.energi = intervensi_info.energi

    db.commit()
    db.refresh(intervensi)

    return intervensi


def delete_intervensi_service(
    db: Session,
    intervensi_id: int
):
    intervensi = db.query(Intervensi
    ).filter(Intervensi.id == intervensi_id
    ).filter(Intervensi.deleted_at == None).first()

    if not intervensi:
        raise HTTPException(status_code=404, detail="Intervensi not found")
    
    intervensi.deleted_at = func.now()

    db.commit()
    db.refresh(intervensi)

    return intervensi
