from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import JadwalKonseling, RekamPasien

from datetime import date

def get_jadwal_konsultasi_dashboard(db: Session, user_id: int):

    today = date.today()

    jadwal = (
        db.query(JadwalKonseling)
        .filter(JadwalKonseling.pasien_id == user_id)
        .filter(JadwalKonseling.tanggal_konseling >= today)
        .filter(JadwalKonseling.deleted_at.is_(None))
        .all()
    )

    return {
        "data": [
            {
                "id": item.id,
                "tanggal_konseling": item.tanggal_konseling,
                "status": item.status,
                "nama_konselor": item.konselor.nama if item.konselor else "",
                "day_of_week": item.jadwal_tersedia.day_of_week if item.jadwal_tersedia else "",
                "start_time": item.jadwal_tersedia.start_time if item.jadwal_tersedia else None,
                "jadwal_tersedia_id": item.jadwal_tersedia_id,
            }
            for item in jadwal
        ]
    }

def get_intervensi_dashboard(db: Session, user_id: int):

   intervensi = (
    db.query(
        RekamPasien.jenis_diet, 
        RekamPasien.karbohidrat, 
        RekamPasien.edukasi_intervensi,
        RekamPasien.protein,
        RekamPasien.prinsip_intervensi,
        RekamPasien.tanggal_asesmen,
        RekamPasien.id,
        RekamPasien.status,
        RekamPasien.tujuan_intervensi,
        RekamPasien.prinsip_intervensi
        )
        .filter(RekamPasien.pasien_id == user_id)
        .filter(RekamPasien.deleted_at.is_(None))
        .order_by(RekamPasien.tanggal_asesmen.desc())
        .limit(10)
    )

   result = [row._mapping for row in intervensi]
   return {
       "data":result
   }



    