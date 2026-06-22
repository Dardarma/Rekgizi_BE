from fastapi import HTTPException
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models import JadwalKonseling, RekamPasien, Article, Intervensi

from datetime import date, datetime

from app.models.users import User


def _period_bounds(year: int | None = None, month: int | None = None):
    today = date.today()
    selected_year = year or today.year
    selected_month = month or today.month
    start = datetime(selected_year, selected_month, 1)
    if selected_month == 12:
        end = datetime(selected_year + 1, 1, 1)
    else:
        end = datetime(selected_year, selected_month + 1, 1)
    return selected_year, selected_month, start, end


def getInformationYearly(
    db: Session,
    user_id: int,
    year: int | None = None,
    month: int | None = None,
):
    selected_year, selected_month, start, end = _period_bounds(year, month)

    total_case = db.query(RekamPasien).filter(
        RekamPasien.deleted_at.is_(None),
        RekamPasien.tanggal_asesmen >= start,
        RekamPasien.tanggal_asesmen < end,
    ).count()

    total_approved = db.query(RekamPasien).filter(
        RekamPasien.deleted_at.is_(None),
        RekamPasien.tanggal_asesmen >= start,
        RekamPasien.tanggal_asesmen < end,
        RekamPasien.status == "disetujui",
    ).count()

    total_appoinment = db.query(JadwalKonseling)\
        .filter(JadwalKonseling.konselor_id == user_id)\
        .filter(JadwalKonseling.status == "approved")\
        .filter(JadwalKonseling.deleted_at.is_(None))\
        .filter(JadwalKonseling.tanggal_konseling >= start.date())\
        .filter(JadwalKonseling.tanggal_konseling < end.date())\
        .count()
    
    total_article = db.query(Article)\
        .filter(Article.deleted_at.is_(None))\
        .filter(Article.created_at >= start)\
        .filter(Article.created_at < end)\
        .count()

    return {
        "tahun": selected_year,
        "bulan": selected_month,
        "total_case": total_case,
        "total_approved": total_approved,
        "total_appoinment": total_appoinment,
        "total_article": total_article
    }


def getRekamPasienDashboardService(
    db: Session,
    year: int | None = None,
    month: int | None = None,
):
    _, _, start, end = _period_bounds(year, month)
    
    rekam_pasien = (db.query(
        RekamPasien.status,
        RekamPasien.id,
        RekamPasien.tanggal_asesmen,
        User.nama.label("nama_pasien")
    )
    .join(User, RekamPasien.pasien_id == User.id)
    .filter(
        RekamPasien.deleted_at.is_(None),
        RekamPasien.tanggal_asesmen >= start,
        RekamPasien.tanggal_asesmen < end,
    )
    .order_by(RekamPasien.tanggal_asesmen.desc())
    .limit(10)
    )
    
    result = [dict(row._mapping) for row in rekam_pasien]
    
    
    return{
        "data":result
    }
    
def getPersebaranKasusService(
    db: Session,
    year: int | None = None,
    month: int | None = None,
):
    _, _, start, end = _period_bounds(year, month)
    
    rekamPasien = (
    db.query(
        RekamPasien.intervensi_id,
        func.count(RekamPasien.id).label("total")
    )
    .filter(
        RekamPasien.tanggal_asesmen >= start,
        RekamPasien.tanggal_asesmen < end,
        RekamPasien.deleted_at.is_(None),
        RekamPasien.intervensi_id.is_not(None),
    )
    .group_by(RekamPasien.intervensi_id)
    .all()
    )

    data_map = {intervensi_id: total for intervensi_id, total in rekamPasien}

    intervensi = (
        db.query(Intervensi.id, Intervensi.jenis_diet)
        .filter(Intervensi.deleted_at.is_(None))
        .order_by(Intervensi.protein, Intervensi.id)
        .all()
    )

    categories = [item.jenis_diet for item in intervensi]
    data = [data_map.get(item.id, 0) for item in intervensi]
    
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

def getRekamPasienPerPekan(
    db: Session,
    year: int | None = None,
    month: int | None = None,
):
    _, _, start, end = _period_bounds(year, month)
    
    week_expression = func.floor(
        (extract('day', RekamPasien.tanggal_asesmen) - 1) / 7
    ) + 1

    rekam_pasien = (
        db.query(
            week_expression.label("minggu"),
            func.count(RekamPasien.id).label("total")
        )
        .filter(
            RekamPasien.deleted_at.is_(None),
            RekamPasien.tanggal_asesmen >= start,
            RekamPasien.tanggal_asesmen < end,
        )
        .group_by(week_expression)
        .order_by(week_expression)
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

def getUsiaPerTahunService(
    db: Session,
    year: int | None = None,
    month: int | None = None,
):
    _, _, start, end = _period_bounds(year, month)
    
    rekam_pasien = (
        db.query(RekamPasien)
        .join(RekamPasien.pasien)
        .filter(
            RekamPasien.deleted_at.is_(None),
            RekamPasien.tanggal_asesmen >= start,
            RekamPasien.tanggal_asesmen < end,
        )
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
        
        assessment_date = item.tanggal_asesmen.date()
        umur = (
            assessment_date.year
            - tanggal_lahir.year
            -(
                (assessment_date.month, assessment_date.day)
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
            ">= 70 tahun"
        ]
    }
