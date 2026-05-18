from sqlalchemy.orm import Session, joinedload

from app.ml.ml_service import predict_cluster_service
from app.models.diagnosa import Diagnosa
from app.models.diagnosa_pasien import DiagnosaPasien
from app.models.intevensi import Intervensi
from app.models.parameter import Parameter
from app.models.rekam_pasien import RekamPasien
from app.models.rekam_pasien_parameter import RekamPasienParameter
from app.schemas.intervensi_schema import IntervensiInfo
from app.schemas.rekam_pasien_schema import IntervensiRekamPasienRequest, RekamPasienBase
from app.schemas.summary_schema import DiagnosaSummaryItem, ParameterSummaryItem, RekamPasienSummary
from app.utils.helpers.calculate_age import hitung_usia
from sqlalchemy.orm import joinedload


def putIntervensiPasienService(
    db: Session,
    rekam_pasien_id: int,
    payload: IntervensiRekamPasienRequest
):
    query = (
        db.query(RekamPasien)
        .options(joinedload(RekamPasien.pasien))
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
    
    return RekamPasienBase(
        id=query.id,
        pasien_id=query.pasien_id,
        nama_pasien=query.pasien.nama if query.pasien else None,
        tanggal_asesmen=query.tanggal_asesmen,
        status=query.status,
        intervensi_id=query.intervensi_id,
        tujuan_intervensi=query.tujuan_intervensi,
        prinsip_intervensi=query.prinsip_intervensi,
        edukasi_intervensi=query.edukasi_intervensi,
        karbohidrat=query.karbohidrat,
        protein=query.protein,
        energi=query.energi
    )


def get_rekam_pasien_summary(db, rekam_pasien_id: int):
    from sqlalchemy.orm import with_loader_criteria

    result = (
        db.query(RekamPasien)
        .options(
            joinedload(RekamPasien.pasien),
            joinedload(RekamPasien.rekam_pasien_parameter)
                .joinedload(RekamPasienParameter.parameter),
            with_loader_criteria(RekamPasienParameter, RekamPasienParameter.deleted_at.is_(None)),
            with_loader_criteria(Parameter, Parameter.deleted_at.is_(None)),
            joinedload(RekamPasien.diagnosa_pasien)
                .joinedload(DiagnosaPasien.diagnosa),
            with_loader_criteria(DiagnosaPasien, DiagnosaPasien.deleted_at.is_(None)),
            with_loader_criteria(Diagnosa, Diagnosa.deleted_at.is_(None)),
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

from fastapi import HTTPException


def prediksiIntervensi(db: Session, rekam_pasien_id: int):

    query = (
        db.query(RekamPasien)
        .options(
            joinedload(RekamPasien.pasien),
            joinedload(RekamPasien.rekam_pasien_parameter)
            .joinedload(RekamPasienParameter.parameter)
        )
        .filter(
            RekamPasien.id == rekam_pasien_id,
            RekamPasien.deleted_at.is_(None)
        )
        .first()
    )

    if not query:
        raise HTTPException(
            status_code=404,
            detail="Rekam pasien tidak ditemukan"
        )

    validateImportantParameters(db, query)

    try:

        features = map_to_features(query)

        cluster = predict_cluster_service(features)

        intervensi = get_intervensi_by_cluster(db, cluster)

        result = {
            "intervensi_id": intervensi.id,
            "jenis_diet": intervensi.jenis_diet,
            "tujuan": intervensi.tujuan,
            "edukasi": intervensi.edukasi,
            "prinsip": intervensi.prinsip,
            "protein": intervensi.protein,
            "energi": intervensi.energi,
            "karbohidrat": intervensi.karbohidrat,
        }

        payload_obj = IntervensiRekamPasienRequest(**result)

        data = putIntervensiPasienService(
            db,
            rekam_pasien_id,
            payload_obj
        )

        return data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


def convert_value(value, target_type):
    if value is None:
        return None

    value = str(value).strip().lower()

    if value in ["", "-", "none", "null"]:
        return None

    if target_type == int:
        try:
            return int(float(value))  # handle "6.38"
        except:
            return None

    if target_type == float:
        try:
            return float(value)
        except:
            return None

    if target_type == bool:
        return value in ["1", "true", "ya", "yes"]

    return value

def map_to_features(rekam_pasien):
    result = {}

    temp = {}

    for item in rekam_pasien.rekam_pasien_parameter:
        nama_db = item.parameter.nama
        raw_value = item.jawaban

        temp[nama_db] = raw_value


    result["BB"] = convert_value(temp.get("Berat badan"), float)
    result["Creatinin"] = convert_value(temp.get("Creatinine"), float)
    result["Ureum"] = convert_value(temp.get("Ureum"), float)

    result["Kelebihan Natrium"] = convert_value(
        temp.get("Konsumsi Natrium Berlebih"), bool
    )

    result["Kelebihan Karbohidrat"] = convert_value(
        temp.get("Konsumsi Karbohidrat Berlebih"), bool
    )

    result["Edema"] = convert_value(
        temp.get("Edema kaki"), bool
    )

    result["Tekanan sistolik"] = convert_value(
        temp.get("Tekanan sistolik"), float
    )

    result["Tekanan Diastolik"] = convert_value(
        temp.get("Tekanan Diastolik"), float
    )


    sistolik = result.get("Tekanan sistolik", 0) or 0
    diastolik = result.get("Tekanan Diastolik", 0) or 0

    result["Darah Tinggi"] = int(
        (sistolik > 120) or (diastolik > 80)
    )


    gdp = convert_value(temp.get("Glukosa darah puasa"), float) or 0
    gds = convert_value(temp.get("Glukosa sewaktu"), float) or 0
    hba1c = convert_value(temp.get("HbA1c"), float) or 0
    riwayat = convert_value(temp.get("Riwayat Diabetes"), bool)

    result["Diabetes"] = int(
        (gdp >= 126) or
        (gds >= 200) or
        (hba1c >= 6.5) or
        (riwayat == 1)
    )

    return result

CLUSTER_DIET_MAP = {
    0: "Diet Rendah Protein 30 g",
    1: "Diet Rendah Protein 40 g",
    2: "Diet Dialisa 65 g",
    3: "Diet Dialisa 70 g",
    4: "Diet Rendah Protein 35 g",
    5: "Diet Dialisa 60 g",
}

def get_intervensi_by_cluster(db, cluster: int):
    jenis_diet = CLUSTER_DIET_MAP.get(cluster)

    if not jenis_diet:
        raise ValueError(f"Cluster tidak valid: {cluster}")

    intervensi = (
        db.query(Intervensi)
        .filter(
            Intervensi.jenis_diet == jenis_diet,
            Intervensi.deleted_at.is_(None)
        )
        .first()
    )

    if not intervensi:
        raise ValueError(f"Intervensi tidak ditemukan untuk diet: {jenis_diet}")

    return IntervensiInfo(
        id=intervensi.id,
        jenis_diet=intervensi.jenis_diet,
        tujuan=intervensi.tujuan,
        prinsip=intervensi.prinsip,
        edukasi=intervensi.edukasi,
        protein=intervensi.protein,
        energi=intervensi.energi,
        karbohidrat=intervensi.karbohidrat
    )

def build_payload_from_intervensi(intervensi: IntervensiInfo):
    return {
        "intervensi_id": intervensi.id,
        "jenis_diet": intervensi.jenis_diet,
        "tujuan": intervensi.tujuan,
        "edukasi": intervensi.edukasi,
        "prinsip": intervensi.prinsip,
        "protein": intervensi.protein,
        "energi": intervensi.energi,
        "karbohidrat": intervensi.karbohidrat
    }

def validateImportantParameters(db: Session, rekam_pasien):

    important_parameters = (
        db.query(Parameter)
        .filter(
            Parameter.important == True,
            Parameter.deleted_at.is_(None)
        )
        .all()
    )

    rekam_parameter_map = {
        item.parameter.id: item
        for item in rekam_pasien.rekam_pasien_parameter
    }

    missing_parameters = []

    for parameter in important_parameters:

        rekam_param = rekam_parameter_map.get(parameter.id)

        if (
            rekam_param is None or
            rekam_param.jawaban is None or
            str(rekam_param.jawaban).strip() == ""
        ):

            missing_parameters.append({
                "parameter_id": parameter.id,
                "parameter_nama": parameter.nama,
                "kategori": parameter.kategori
            })

    if missing_parameters:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Parameter penting belum lengkap",
                "missing_parameters": missing_parameters
            }
        )