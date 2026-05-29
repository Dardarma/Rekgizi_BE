from fastapi import HTTPException
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models import JadwalKonseling, RekamPasien, Article, Intervensi

from datetime import date

from app.models.users import User

def getInformationYearly(db:Session, user_id:int):
    current_year = date.today().year

    total_case = db.query(RekamPasien).filter(
        func.extract('year', RekamPasien.tanggal_asesmen) == current_year
    ).count()

    total_approved = db.query(RekamPasien).filter(
        func.extract('year', RekamPasien.tanggal_asesmen) == current_year,
        RekamPasien.status == "disetujui"
    ).count()

    total_appoinment = db.query(JadwalKonseling)\
        .filter(JadwalKonseling.konselor_id == user_id)\
        .filter(JadwalKonseling.status == "approved")\
        .filter(JadwalKonseling.deleted_at.is_(None))\
        .filter(func.extract('year', JadwalKonseling.tanggal_konseling) == current_year)\
        .count()
    
    total_article = db.query(Article)\
        .filter(Article.deleted_at.is_(None))\
        .count()

    return {
        "tahun": current_year,
        "total_case": total_case,
        "total_approved": total_approved,
        "total_appoinment": total_appoinment,
        "total_article": total_article
    }


def getRekamPasienDashboardService(db:Session):
    
    rekam_pasien = (db.query(
        RekamPasien.status,
        RekamPasien.id,
        RekamPasien.tanggal_asesmen,
        User.nama.label("nama_pasien")
    )
    .join(User, RekamPasien.pasien_id == User.id)
    .filter(RekamPasien.deleted_at.is_(None))
    .order_by(RekamPasien.tanggal_asesmen.desc())
    .limit(10)
    )
    
    result = [dict(row._mapping) for row in rekam_pasien]
    
    
    return{
        "data":result
    }
    
def getPersebaranKasusService(db:Session):
    
    current_month = date.today().month
    current_year = date.today().year
    
    rekamPasien = (
    db.query(
        RekamPasien.jenis_diet,
        func.count(RekamPasien.id).label("total")
    )
    .filter(
        func.extract('month', RekamPasien.tanggal_asesmen) == current_month,
        func.extract('year', RekamPasien.tanggal_asesmen) == current_year,
        RekamPasien.deleted_at.is_(None)
    )
    .group_by(RekamPasien.jenis_diet)
    .all()
    )

    data_map = {item[0]: item[1] for item in rekamPasien}

    intervensi = (
        db.query(Intervensi.jenis_diet)
        .filter(Intervensi.deleted_at.is_(None))
        .all()
    )

    categories = [item[0] for item in intervensi]
    data = [data_map.get(category, 0) for category in categories]
    
    response = {
        "seriesData":[
            {
                "name": "jumlah Pasien",
                "data": data
            }
        ],
        "categories": categories
    }
    
    return response

def getRekamPasienPerPekan(db:Session):
    current_month = date.today().month
    current_year = date.today().year

    
    
    rekam_pasien = (
        db.query(
            (
                ((extract('day', RekamPasien.tanggal_asesmen) - 1) / 7) + 1
            ).label("minggu"),
            func.count(RekamPasien.id).label("total")
        )
        .filter(
            RekamPasien.deleted_at.is_(None),
            extract('month', RekamPasien.tanggal_asesmen) == current_month,
            extract('year', RekamPasien.tanggal_asesmen) == current_year,
        )
        .group_by("minggu")
        .order_by("minggu")
        .all()
    )
    
    minggu_map = {
        int(item[0]): item[1]
        for item in rekam_pasien
    }
    
    categories = [
        "Minggu 1",
        "Minggu 2",
        "Minggu 3",
        "Minggu 4",
        "Minggu 5",
    ]
    
    data = [
        minggu_map.get(1, 0),
        minggu_map.get(2, 0),
        minggu_map.get(3, 0),
        minggu_map.get(4, 0),
        minggu_map.get(5, 0),
    ]
    
    return{
        "seriesData": [
            {
                "name":"Jumlah Pasien",
                "data": data
            }
        ],
        "categories":categories
    }

def getUsiaPerTahunService(db:Session):
    
    today = date.today()
    
    rekam_pasien = (
        db.query(RekamPasien)
        .join(RekamPasien.pasien)
        .filter(RekamPasien.deleted_at.is_(None))
        .all()
    )
    
    usia_krg_40 = 0
    usia_40_49 = 0
    usia_50_59 = 0
    usia_60_69 = 0
    usia_lbh_70 = 0
    
    for item in rekam_pasien:
        
        tanggal_lahir = item.pasien.tanggal_lahir
        
        if not tanggal_lahir:
            continue
        
        umur = (
            today.year
            - tanggal_lahir.year
            -(
                (today.month, today.day)
                < (tanggal_lahir.month, tanggal_lahir.day)
            )
        )
        
        if umur < 40:
            usia_krg_40 += 1
        elif 40 <= umur < 50:
            usia_40_49 += 1
        elif 50 <= umur < 60:
            usia_50_59 += 1
        elif 60 <= umur < 70:
            usia_60_69 += 1
        elif umur >= 70:
            usia_lbh_70 +=1
    
    return{
        "seriesData":[
            {
                "name":"jumlah Kasus",
                "data":[
                    usia_krg_40,
                    usia_40_49,
                    usia_50_59,
                    usia_60_69,
                    usia_lbh_70
                ]
            }
        ],
        "categories":[
            "< 40 tahun",
            "40 - 49 tahun",
            "50 - 59 tahun",
            "60 - 69 tahun",
            "70 > tahun"
        ]
    }
    
    

    