from sqlalchemy.orm import Session, joinedload

from app.ml.ml_v2.ml_service import ModelInputError, predict_diet_service
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
        jenis_diet=query.jenis_diet,
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

    try:
        features = map_to_features(query)
        recommendation = predict_diet_service(features)
        intervensi = get_intervensi_by_recommendation(db, recommendation)

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

    except HTTPException:
        raise
    except ModelInputError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) from e


def convert_value(value, target_type):
    if value is None:
        # Default boolean to 0 (no/false) if not provided
        if target_type == bool:
            return 0
        return None

    value = str(value).strip().lower()

    if value in ["", "-", "none", "null"]:
        # Default boolean to 0 (no/false) if empty
        if target_type == bool:
            return 0
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
        if value in ["1", "true", "ya", "yes"]:
            return 1
        if value in ["0", "false", "tidak", "no"]:
            return 0
        # Default to 0 (no/false) if value doesn't match any known pattern
        return 0

    return value

def map_to_features(rekam_pasien):
    temp = {}

    for item in rekam_pasien.rekam_pasien_parameter:
        if item.deleted_at is not None or item.parameter is None:
            continue
        nama_db = item.parameter.nama.strip().casefold()
        temp[nama_db] = item.jawaban

    def get_parameter(*names):
        for name in names:
            value = temp.get(name.casefold())
            if value is not None and str(value).strip() != "":
                return value
        return None

    result = {
        "BB": convert_value(get_parameter("Berat badan", "BB"), float),
        "Ureum": convert_value(get_parameter("Ureum"), float),
        "Creatinin": convert_value(get_parameter("Creatinine", "Creatinin"), float),
        "Kelebihan Natrium": convert_value(
            get_parameter("Konsumsi Natrium Berlebih", "Kelebihan Natrium"), bool
        ),
        "Kelebihan Karbohidrat": convert_value(
            get_parameter("Konsumsi Karbohidrat Berlebih", "Kelebihan Karbohidrat"), bool
        ),
        "Edema": convert_value(get_parameter("Edema kaki", "Edema"), bool),
    }

    sistolik = convert_value(get_parameter("Tekanan Sistolik"), float)
    diastolik = convert_value(get_parameter("Tekanan Diastolik"), float)
    tekanan_darah = get_parameter("Tekanan darah", "Tensi")
    if (sistolik is None or diastolik is None) and tekanan_darah is not None:
        try:
            raw_sistolik, raw_diastolik = str(tekanan_darah).split("/", maxsplit=1)
            sistolik = sistolik if sistolik is not None else float(raw_sistolik.strip())
            diastolik = diastolik if diastolik is not None else float(raw_diastolik.strip())
        except (TypeError, ValueError):
            pass

    result["Tekanan_Sistolik"] = sistolik
    result["Tekanan_Diastolik"] = diastolik

    if sistolik is not None and diastolik is not None:
        result["Darah Tinggi"] = int((sistolik > 120) or (diastolik > 80))
    else:
        result["Darah Tinggi"] = None

    gdp = convert_value(get_parameter("Glukosa darah puasa"), float)
    gds = convert_value(get_parameter("Glukosa Sewaktu"), float)
    hba1c = convert_value(get_parameter("HgbA1c", "HbA1c"), float)
    riwayat = convert_value(get_parameter("Riwayat Diabetes", "Diabetes"), bool)
    diabetes_sources = [gdp, gds, hba1c, riwayat]
    if any(value is not None for value in diabetes_sources):
        result["Diabetes"] = int(
            (gdp is not None and gdp >= 126)
            or (gds is not None and gds >= 200)
            or (hba1c is not None and hba1c >= 6.5)
            or riwayat == 1
        )
    else:
        result["Diabetes"] = None

    return result

MODEL_TO_SEEDER_DIET = {
    "RP 30": "Diet Ginjal Rendah Protein 30 g",
    "RP 35": "Diet Ginjal Rendah Protein 35 g",
    "RP 40": "Diet Ginjal Rendah Protein 40 g",
    "Dialisa 60": "Diet Ginjal Dialisa Protein 60 g",
    "Dialisa 65": "Diet Ginjal Dialisa Protein 65 g",
    "Dialisa 70": "Diet Ginjal Dialisa Protein 70 g",
}

def get_intervensi_by_recommendation(db, recommendation: str):
    jenis_diet = MODEL_TO_SEEDER_DIET.get(recommendation.strip())
    if jenis_diet is None:
        raise ValueError(f"Rekomendasi model tidak dikenali: {recommendation}")

    intervensi = (
        db.query(Intervensi)
        .filter(
            Intervensi.jenis_diet == jenis_diet,
            Intervensi.deleted_at.is_(None)
        )
        .first()
    )

    if not intervensi:
        raise ValueError(
            f"Intervensi tidak ditemukan untuk diet: {jenis_diet}. "
            "Jalankan `python -m app.seeder.intervensi_seed`."
        )

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

def setujuiIntervensiService(
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
        )
        .first()
    )

    if not query:
        raise HTTPException(
            status_code=404,
            detail="Rekam pasien tidak ditemukan"
        )

    query.intervensi_id = payload.intervensi_id
    query.jenis_diet = payload.jenis_diet
    query.tujuan_intervensi = payload.tujuan
    query.edukasi_intervensi = payload.edukasi
    query.prinsip_intervensi = payload.prinsip
    query.protein = payload.protein
    query.energi = payload.energi
    query.karbohidrat = payload.karbohidrat
    query.status = "disetujui"

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
        jenis_diet=query.jenis_diet,
        karbohidrat=query.karbohidrat,
        protein=query.protein,
        energi=query.energi
    )
