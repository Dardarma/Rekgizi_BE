from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Diagnosa
from app.schemas.diagnosa_schema import diagnosaBasicInfo, diagnosaInfo
from fastapi import HTTPException

def get_diagnosa_service(
    db:Session
):
    diagnosa = db.query(Diagnosa).filter(Diagnosa.deleted_at == None).all()
    
    if not diagnosa:
        raise HTTPException(status_code=404, detail="Diagnosa not Found")
    
    return diagnosa

def create_diagnosa_service(
    db: Session,
    payload: diagnosaBasicInfo
):
    new_diagnosa = Diagnosa(
        kode = payload.kode,
        diagnosa = payload.diagnosa
    )
    
    db.add(new_diagnosa)
    db.commit()
    db.refresh(new_diagnosa)
    
    return new_diagnosa

def edit_diagnosa_service(
    db:Session,
    diagnosa_id: int,
    payload: diagnosaBasicInfo
):
    diagnosa = db.query(Diagnosa
    ).filter(Diagnosa.id == diagnosa_id
    ).filter(Diagnosa.deleted_at == None).first()
    
    if not diagnosa:
        raise HTTPException(status_code=404, detail="Diagnosa not Found")
    
    diagnosa.kode = payload.kode
    diagnosa.diagnosa = payload.diagnosa

    db.commit()
    db.refresh(diagnosa)
    
    return diagnosa

def delete_diagnosa_service(
    db:Session,
    diagnosa_id: int
):
    diagnosa = db.query(Diagnosa
    ).filter(Diagnosa.id == diagnosa_id
    ).filter(Diagnosa.deleted_at == None).first()
    
    if not diagnosa:
        raise HTTPException(status_code=404, detail="Diagnosa not Found")
    
    diagnosa.deleted_at = func.now()
    
    db.commit()
    db.refresh(diagnosa)
    
    return diagnosa
    
    
    
