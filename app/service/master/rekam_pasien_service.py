from fastapi  import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import RekamPasien
from app.models.users import RoleEnum, User
from app.schemas.rekam_pasien_schema import RekamPasienBase, RekamPasienCreate, RekamPasienUpdate

def get_rekam_pasien_by_user_service(
    db: Session,
    pasien_id: int 
):
    
    rekam_pasien = (
        db.query(RekamPasien,
         User.nama.label("nama_pasien")        
        )
        .join(User, RekamPasien.pasien_id == User.id)
        .filter(RekamPasien.deleted_at.is_(None))
        .filter(RekamPasien.pasien_id == pasien_id)
        .all()
    )

    if not rekam_pasien:
        raise HTTPException(status_code=404, detail="Rekam pasien not found")
    
    result = []
    for rp, nama_pasien in rekam_pasien:
        result.append({
            "id": rp.id,
            "pasien_id": rp.pasien_id,
            "nama_pasien": nama_pasien,
            "tanggal_asesmen": rp.tanggal_asesmen,
            "status": rp.status,
        })
    
    return result

def get_rekam_pasien_me_service(
    db: Session,
    user_id: int,
):
    rekam_pasien = (
        db.query(
            RekamPasien,
            User.nama.label("nama_pasien") )
        .join(User, RekamPasien.pasien_id == User.id)
        .filter(RekamPasien.pasien_id == user_id)
        .filter(RekamPasien.deleted_at.is_(None))
        .all()
    )


    if not rekam_pasien:
        raise HTTPException(status_code=404, detail="Rekam pasien not found")

    result = []
    for rp, nama_pasien in rekam_pasien:
        result.append({         
            "id": rp.id,
            "pasien_id": rp.pasien_id,
            "nama_pasien": nama_pasien,
            "tanggal_asesmen": rp.tanggal_asesmen,
            "status": rp.status,
        })

    return result

def get_rekam_pasien_by_id_service(
    db: Session,
    user_id: int,
    role: str = None,
    rekam_pasien_id: int = None,
):
    rekam_pasien = (
        db.query(RekamPasien)
        .filter(
            RekamPasien.id == rekam_pasien_id,
            RekamPasien.deleted_at.is_(None)
        )
        .first()
    )

    
    if role == "pasien" and rekam_pasien.pasien_id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    if not rekam_pasien:
        raise HTTPException(status_code=404, detail="Rekam pasien not found")
    
    nama_pasien = rekam_pasien.pasien.nama

    return {
    "id": rekam_pasien.id,
    "pasien_id": rekam_pasien.pasien_id,
    "nama_pasien": rekam_pasien.pasien.nama if rekam_pasien.pasien else None,
    "tanggal_asesmen": rekam_pasien.tanggal_asesmen,
    "status": rekam_pasien.status,
    "intervensi_id": rekam_pasien.intervensi_id,
    "tujuan_intervensi": rekam_pasien.tujuan_intervensi,
    "prinsip_intervensi": rekam_pasien.prinsip_intervensi,
    "edukasi_intervensi": rekam_pasien.edukasi_intervensi,
    "karbohidrat": rekam_pasien.karbohidrat,
    "protein": rekam_pasien.protein,
    "energi": rekam_pasien.energi,
    }

def post_rekam_pasien_service(
        db:Session,
        payload: RekamPasienBase,
):
    pasien = (db.query(User).filter(
        User.id == payload.pasien_id,
        User.deleted_at.is_(None)
    )).first()

    if not pasien:
        raise HTTPException(status_code=404, detail="Pasien not found")
    
    if pasien.role != RoleEnum.pasien:
        raise HTTPException(status_code=400, detail="User is not a pasien")
    
    new_rekam_pasien = RekamPasien(
        pasien_id=payload.pasien_id,
        tanggal_asesmen=payload.tanggal_assesmen,
        status=payload.status,
        intervensi_id=payload.intervensi_id,
        tujuan_intervensi=payload.tujuan_intervensi,
        prinsip_intervensi=payload.prinsip_intervensi,
        edukasi_intervensi=payload.edukasi_intervensi,
    )

    db.add(new_rekam_pasien)
    db.commit()
    db.refresh(new_rekam_pasien)

    return{
        "id": new_rekam_pasien.id,
        "pasien_id": new_rekam_pasien.pasien_id,
        "nama_pasien": pasien.nama,
        "tanggal_asesmen": new_rekam_pasien.tanggal_asesmen,
        "status": new_rekam_pasien.status,
    }

def update_rekam_pasien_service(
        db: Session,
        payload: RekamPasienUpdate,
        rekam_pasien_id: int,
):
    rekam_pasien = db.query(
        RekamPasien,      
    ).filter(
        RekamPasien.id == rekam_pasien_id,
        RekamPasien.deleted_at.is_(None)
    ).first()

    if not rekam_pasien:
        raise HTTPException(status_code=404, detail="Rekam pasien not found")

    rekam_pasien.pasien_id = payload.pasien_id
    rekam_pasien.tanggal_asesmen = payload.tanggal_asesmen
    rekam_pasien.status = payload.status

    db.commit()
    db.refresh(rekam_pasien)

    nama_pasien = rekam_pasien.pasien.nama

    return{
        "id": rekam_pasien.id,
        "pasien_id": rekam_pasien.pasien_id,
        "nama_pasien": nama_pasien,
        "tanggal_asesmen": rekam_pasien.tanggal_asesmen,
        "status": rekam_pasien.status,
    }

def delete_rekam_pasien_service(
        db: Session,
        rekam_pasien_id: int,
):
    rekam_pasien = db.query(RekamPasien).filter(
        RekamPasien.id == rekam_pasien_id,
        RekamPasien.deleted_at.is_(None)
    ).first()

    if not rekam_pasien:
        raise HTTPException(status_code=404, detail="Rekam pasien not found")

    rekam_pasien.deleted_at = func.now()

    nama_pasien = rekam_pasien.pasien.nama

    db.commit()

    return {
        "id": rekam_pasien.id,
        "pasien_id": rekam_pasien.pasien_id,
        "nama_pasien": nama_pasien,
        "tanggal_asesmen": rekam_pasien.tanggal_asesmen,
        "status": rekam_pasien.status,
    }