from inspect import Parameter

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func


from app.models.diagnosa_pasien import DiagnosaPasien
from app.models.rekam_pasien import RekamPasien
from app.models.rekam_pasien_parameter import RekamPasienParameter
from app.schemas.rekam_pasien_schema import  IntervensiRekamPasienRequest
from app.schemas.summary_schema import DiagnosaSummaryItem, ParameterSummaryItem, RekamPasienSummary
from app.utils.helpers.calculate_age import hitung_usia

def putIntervensiPasienService(
    db: Session,
    rekam_pasien_id: int,
    payload: IntervensiRekamPasienRequest
):
    query = (
        db.query(RekamPasien)
        .filter(
            RekamPasien.id == rekam_pasien_id,
            RekamPasien.deleted_at.is_(None)
        ).first()
        )
    
    query.intervensi_id = payload.intervensi_id
    query.jenis_diet = payload.jenis_diet
    query.tujuan_intervensi = payload.tujuan
    query.edukasi_intervensi = payload.edukasi
    query.prinsip_intervensi = payload.prinsip
    query.protein = payload.protein
    query.energi = payload.energi
    query.karbohidrat = payload.karbohidrat
    query.status = 'ditinjau'
    
    db.commit()
    db.refresh(query)
    
    return query

from sqlalchemy.orm import joinedload

def get_rekam_pasien_summary(db, rekam_pasien_id: int):
    result = (
        db.query(RekamPasien)
        .options(
            joinedload(RekamPasien.pasien),
            joinedload(RekamPasien.rekam_pasien_parameter)
                .joinedload(RekamPasienParameter.parameter),
            joinedload(RekamPasien.diagnosa_pasien)
                .joinedload(DiagnosaPasien.diagnosa)
        )
        .filter(
            RekamPasien.id == rekam_pasien_id,
            RekamPasien.deleted_at.is_(None)
        )
        .first()
    )

    return result
    
def map_to_summary(result: RekamPasien) -> RekamPasienSummary:
    return RekamPasienSummary(
            nama=result.pasien.nama,
            jenis_kelamin=result.pasien.jenis_kelamin,
            alamat=result.pasien.alamat,
            usia=hitung_usia(result.pasien.tanggal_lahir),
            tanggal_asesmen=result.tanggal_asesmen,
            status=result.status,
            tujuan_intervensi=result.tujuan_intervensi,
            prinsip_intervensi=result.prinsip_intervensi,
            edukasi_intervensi=result.edukasi_intervensi,
            jenis_diet=result.jenis_diet,
            protein=result.protein,
            energi=result.energi,
            karbohidrat=result.karbohidrat,
            diagnosa=[
                DiagnosaSummaryItem(
                    kode=dp.diagnosa.kode,
                    diagnosa=dp.diagnosa.diagnosa
                )
                for dp in result.diagnosa_pasien
                if dp.diagnosa is not None
            ],
            parameter=[
                ParameterSummaryItem(
                    nama_parameter=rp.parameter.nama if rp.parameter else None,
                    kategori=rp.parameter.kategori if rp.parameter else None,
                    jawaban=rp.jawaban
                )
                for rp in result.rekam_pasien_parameter
                if rp.deleted_at is None
            ]
    )