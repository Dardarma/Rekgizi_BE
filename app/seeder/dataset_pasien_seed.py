"""Seeder pasien dan asesmen dari data_riwayat_fisik_diagnosis.csv.

Jalankan master seeder parameter, opsi parameter, dan diagnosis sebelum
menjalankan modul ini. Data identitas yang tidak tersedia pada sumber
dibuat secara deterministik agar seeder aman dijalankan ulang.
"""

from __future__ import annotations

import csv
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.diagnosa import Diagnosa
from app.models.diagnosa_pasien import DiagnosaPasien
from app.models.intevensi import Intervensi
from app.models.opsi_parameter import OpsiParameter
from app.models.parameter import Parameter
from app.models.rekam_pasien import RekamPasien, statusEnum
from app.models.rekam_pasien_parameter import RekamPasienParameter
from app.models.users import KelaminEnum, RoleEnum, User


SOURCE_FILE = Path(__file__).resolve().parent / "data" / "data_riwayat_fisik_diagnosis.csv"
EXPECTED_COLUMN_COUNT = 39
DATASET_BIRTH_DATES = (
    date(1998, 2, 14),
    date(1993, 7, 21),
    date(1988, 12, 5),
    date(1984, 4, 9),
    date(1981, 10, 17),
    date(1978, 6, 28),
    date(1975, 1, 11),
    date(1972, 8, 23),
    date(1969, 5, 19),
    date(1964, 3, 7),
    date(1961, 9, 30),
    date(1958, 12, 16),
    date(1953, 4, 22),
    date(1948, 11, 3),
    date(1942, 7, 15),
)
BASE_ASSESSMENT_DATE = datetime(2026, 6, 1, 8, 0, 0)
DEFAULT_PASSWORD = "password"
EMAIL_TEMPLATE = "pasien.dataset.{source_id:03d}@example.com"
LEGACY_EMAIL_TEMPLATE = "pasien.dataset.{source_id:03d}@rekgizi.test"
INTERVENTION_LABELS = {
    "RP 30": "Diet Ginjal Rendah Protein 40 g",
    "RP 35": "Diet Ginjal Rendah Protein 30 g",
    "RP 40": "Diet Ginjal Rendah Protein 35 g",
    "Dialisa 60": "Diet Ginjal Dialisa Protein 60 g",
    "Dialisa 65": "Diet Ginjal Dialisa Protein 65 g",
    "Dialisa 70": "Diet Ginjal Dialisa Protein 70 g",
}


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    result = value.strip()
    return result or None


def normalize_boolean(value: str | None) -> str | None:
    value = clean(value)
    if value is None:
        return None

    normalized = value.casefold()
    if normalized in {"true", "ya", "yes", "1"}:
        return "true"
    if normalized in {"false", "tidak", "no", "0"}:
        return "false"
    raise ValueError(f"Nilai boolean tidak dikenali: {value}")


def normalize_text(value: str | None) -> str | None:
    return clean(value)


ParameterNormalizer = Callable[[str | None], str | None]


def first_non_null(
    row: list[str],
    indexes: tuple[int, ...],
    normalizer: ParameterNormalizer,
) -> str | None:
    values = [normalizer(row[index]) for index in indexes]
    non_null_values = [value for value in values if value is not None]
    if len({value.casefold() for value in non_null_values}) > 1:
        raise ValueError(
            f"Nilai kolom duplikat bertentangan pada baris sumber {row[0]}: "
            f"{non_null_values}"
        )
    return non_null_values[0] if non_null_values else None

# (nama parameter database, indeks kolom sumber, normalizer)
PARAMETER_SOURCES: tuple[tuple[str, tuple[int, ...], ParameterNormalizer], ...] = (
    ("Berat badan", (1,), normalize_text),
    ("Tinggi badan", (2,), normalize_text),
    ("Ureum", (3,), normalize_text),
    ("Creatinine", (4,), normalize_text),
    ("Konsumsi Natrium Berlebih", (5,), normalize_boolean),
    ("Riwayat Diabetes", (7,), normalize_boolean),
    ("Dispnea", (10,), normalize_boolean),
    ("Anorexia", (11,), normalize_boolean),
    ("Acites", (12,), normalize_boolean),
    ("Nafsu makan menurun", (13,), normalize_boolean),
    ("Mual", (14,), normalize_boolean),
    ("Muntah", (15,), normalize_boolean),
    ("Edema kaki", (16, 9), normalize_boolean),
    ("Kulit mengelupas", (17,), normalize_boolean),
    ("Suhu", (18,), normalize_text),
    ("Jumlah Cairan melalui oral", (19, 24), normalize_text),
    ("Jumlah Cairan dari makanan", (20, 25), normalize_text),
    ("Suplemen/cairan pengganti makanan", (21, 26), normalize_text),
    ("Jumlah makanan", (22, 27), normalize_text),
    ("Jenis makanan", (23, 28), normalize_text),
    ("Pola makan/snack", (29,), normalize_text),
    ("Asupan protein bernilai biologis tinggi", (30,), normalize_text),
    ("Asupan karbohidrat kompleks", (31,), normalize_text),
    ("Asupan karbohidrat sederhana", (32,), normalize_text),
    ("Penggunaan Resep Obat", (33,), normalize_text),
    ("Komplementer/obat alternatif", (34,), normalize_text),
    ("Kesukaan makanan", (35,), normalize_text),
    ("Pendidikan", (36,), normalize_text),
)


def load_source_rows() -> list[list[str]]:
    with SOURCE_FILE.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        header = next(reader)
        rows = [row for row in reader if any(clean(value) for value in row)]

    if len(header) != EXPECTED_COLUMN_COUNT:
        raise ValueError(
            f"Jumlah kolom sumber harus {EXPECTED_COLUMN_COUNT}, ditemukan {len(header)}"
        )

    for row_number, row in enumerate(rows, start=2):
        if len(row) != EXPECTED_COLUMN_COUNT:
            raise ValueError(
                f"Baris CSV {row_number} memiliki {len(row)} kolom; "
                f"seharusnya {EXPECTED_COLUMN_COUNT}"
            )
        if clean(row[0]) is None:
            raise ValueError(f"ID sumber kosong pada baris CSV {row_number}")

    source_ids = [int(row[0]) for row in rows]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("ID sumber pada CSV harus unik")

    return rows


def build_parameter_values(row: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for parameter_name, source_indexes, normalizer in PARAMETER_SOURCES:
        value = first_non_null(row, source_indexes, normalizer)
        if value is not None:
            values[parameter_name] = value

    tension = clean(row[8])
    if tension is not None:
        match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*", tension)
        if match is None:
            raise ValueError(f"Format tensi tidak valid pada ID sumber {row[0]}: {tension}")
        values["Tekanan Sistolik"] = match.group(1)
        values["Tekanan Diastolik"] = match.group(2)

    return values


def normalize_diagnosis_code(raw_code: str) -> str:
    value = raw_code.strip().upper()
    match = re.fullmatch(r"([A-Z]{2})[\s-]*(\d+(?:\.\d+)*)", value)
    if match is None:
        raise ValueError(f"Format kode diagnosis tidak valid: {raw_code}")
    return f"{match.group(1)}-{match.group(2)}"


def parse_diagnosis_codes(value: str | None) -> list[str]:
    value = clean(value)
    if value is None:
        return []
    return list(dict.fromkeys(normalize_diagnosis_code(item) for item in value.split(",")))


def dataset_birth_date(source_id: int) -> date:
    return DATASET_BIRTH_DATES[(source_id - 1) % len(DATASET_BIRTH_DATES)]


def ensure_user(db: Session, source_id: int, password_hash: str) -> tuple[User, bool]:
    email = EMAIL_TEMPLATE.format(source_id=source_id)
    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        if user.deleted_at is not None:
            user.deleted_at = None
        user.tanggal_lahir = dataset_birth_date(source_id)
        return user, False

    legacy_email = LEGACY_EMAIL_TEMPLATE.format(source_id=source_id)
    user = db.query(User).filter(User.email == legacy_email).first()
    if user is not None:
        user.email = email
        if user.deleted_at is not None:
            user.deleted_at = None
        user.tanggal_lahir = dataset_birth_date(source_id)
        return user, False

    user = User(
        role=RoleEnum.pasien,
        nama=f"Pasien Dataset {source_id:03d}",
        jenis_kelamin=KelaminEnum.pria if source_id % 2 else KelaminEnum.wanita,
        alamat={
            "desa": "Data simulasi",
            "kecamatan": "Data simulasi",
            "kota": "Data simulasi",
            "provinsi": "Data simulasi",
            "lengkap": "Alamat asumsi untuk data seeder",
        },
        tanggal_lahir=dataset_birth_date(source_id),
        email=email,
        pass_hash=password_hash,
    )
    db.add(user)
    db.flush()
    return user, True


def ensure_medical_record(
    db: Session,
    user: User,
    source_id: int,
    intervention_label: str | None,
) -> tuple[RekamPasien, bool]:
    assessment_date = BASE_ASSESSMENT_DATE + timedelta(days=source_id - 1)
    record = (
        db.query(RekamPasien)
        .filter(
            RekamPasien.pasien_id == user.id,
            RekamPasien.tanggal_asesmen == assessment_date,
        )
        .first()
    )

    # Versi seeder lama dapat memakai tanggal asesmen berbeda. Karena akun
    # dataset bersifat khusus, gunakan rekam yang sudah ada agar rerun menjadi
    # backfill intervensi_id dan tidak membuat asesmen duplikat.
    if record is None:
        record = (
            db.query(RekamPasien)
            .filter(RekamPasien.pasien_id == user.id)
            .order_by(RekamPasien.id)
            .first()
        )

    canonical_label = INTERVENTION_LABELS.get(intervention_label or "", intervention_label)
    intervention = None
    if canonical_label:
        intervention = (
            db.query(Intervensi)
            .filter(
                Intervensi.jenis_diet == canonical_label,
                Intervensi.deleted_at.is_(None),
            )
            .first()
        )
        if intervention is None:
            raise RuntimeError(
                f"Master intervensi tidak ditemukan untuk '{canonical_label}'. "
                "Jalankan seeder intervensi terlebih dahulu."
            )

    if record is None:
        record = RekamPasien(
            pasien_id=user.id,
            tanggal_asesmen=assessment_date,
            status=statusEnum.disetujui,
        )
        db.add(record)
        db.flush()
        created = True
    else:
        created = False

    record.deleted_at = None
    record.status = statusEnum.disetujui
    record.intervensi_id = intervention.id if intervention else None
    record.jenis_diet = intervention.jenis_diet if intervention else canonical_label
    record.tujuan_intervensi = intervention.tujuan if intervention else None
    record.prinsip_intervensi = intervention.prinsip if intervention else None
    record.edukasi_intervensi = intervention.edukasi if intervention else None
    record.protein = intervention.protein if intervention else None
    record.energi = intervention.energi if intervention else None
    record.karbohidrat = intervention.karbohidrat if intervention else None
    return record, created


def seed_dataset_pasien() -> None:
    rows = load_source_rows()
    db: Session = SessionLocal()

    counters = {
        "users": 0,
        "medical_records": 0,
        "parameters": 0,
        "diagnoses": 0,
    }

    try:
        required_parameter_names = {
            name for name, _, _ in PARAMETER_SOURCES
        } | {"Tekanan Sistolik", "Tekanan Diastolik"}
        parameters = {
            parameter.nama: parameter
            for parameter in db.query(Parameter)
            .filter(
                Parameter.nama.in_(required_parameter_names),
                Parameter.deleted_at.is_(None),
            )
            .all()
        }
        missing_parameters = required_parameter_names - parameters.keys()
        if missing_parameters:
            raise RuntimeError(
                "Parameter master belum lengkap. Jalankan "
                "`python -m app.seeder.parameter_seed` terlebih dahulu. "
                f"Parameter hilang: {sorted(missing_parameters)}"
            )

        options = {
            (option.parameter_id, option.jawaban.casefold()): option
            for option in db.query(OpsiParameter)
            .filter(OpsiParameter.deleted_at.is_(None))
            .all()
            if option.jawaban
        }

        required_diagnosis_codes = {
            code for row in rows for code in parse_diagnosis_codes(row[37])
        }
        diagnoses = {
            diagnosis.kode: diagnosis
            for diagnosis in db.query(Diagnosa)
            .filter(
                Diagnosa.kode.in_(required_diagnosis_codes),
                Diagnosa.deleted_at.is_(None),
            )
            .all()
        }
        missing_diagnoses = required_diagnosis_codes - diagnoses.keys()
        if missing_diagnoses:
            raise RuntimeError(
                "Diagnosis master belum lengkap. Jalankan "
                "`python -m app.seeder.Diagnosa_seed` terlebih dahulu. "
                f"Kode hilang: {sorted(missing_diagnoses)}"
            )

        password_hash = hash_password(DEFAULT_PASSWORD)

        for row in rows:
            source_id = int(row[0])
            user, user_created = ensure_user(db, source_id, password_hash)
            counters["users"] += int(user_created)

            medical_record, record_created = ensure_medical_record(
                db,
                user,
                source_id,
                clean(row[38]),
            )
            counters["medical_records"] += int(record_created)

            existing_parameters = {
                item.parameter_id: item
                for item in db.query(RekamPasienParameter)
                .filter(RekamPasienParameter.rekam_pasien_id == medical_record.id)
                .order_by(RekamPasienParameter.id)
                .all()
            }
            for parameter_name, answer in build_parameter_values(row).items():
                parameter = parameters[parameter_name]
                option = options.get((parameter.id, answer.casefold()))
                item = existing_parameters.get(parameter.id)
                if item is None:
                    item = RekamPasienParameter(
                        rekam_pasien_id=medical_record.id,
                        parameter_id=parameter.id,
                    )
                    db.add(item)
                    existing_parameters[parameter.id] = item
                    counters["parameters"] += 1

                item.jawaban = answer
                item.opsi_parameter_id = option.id if option else None
                item.deleted_at = None

            existing_diagnoses = {
                item.id_diagnosa: item
                for item in db.query(DiagnosaPasien)
                .filter(DiagnosaPasien.id_rekam_pasien == medical_record.id)
                .all()
            }
            for code in parse_diagnosis_codes(row[37]):
                diagnosis = diagnoses[code]
                item = existing_diagnoses.get(diagnosis.id)
                if item is None:
                    item = DiagnosaPasien(
                        id_rekam_pasien=medical_record.id,
                        id_diagnosa=diagnosis.id,
                    )
                    db.add(item)
                    existing_diagnoses[diagnosis.id] = item
                    counters["diagnoses"] += 1
                else:
                    item.deleted_at = None

        db.commit()
        print(
            "Seeder dataset selesai: "
            f"user baru={counters['users']}, "
            f"rekam pasien baru={counters['medical_records']}, "
            f"parameter baru={counters['parameters']}, "
            f"diagnosis baru={counters['diagnoses']}."
        )
        print(
            "Tanggal lahir pasien dataset dibuat bervariasi sesuai kelompok usia; "
            "nilai null tidak dibuat sebagai rekam_pasien_parameter."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_all_dataset_dependencies() -> None:
    """Jalankan seluruh master data dan dataset pasien dalam satu perintah."""
    from app.seeder.Diagnosa_seed import seed_diagnosa
    from app.seeder.intervensi_seed import seed_intervensi
    from app.seeder.opsi_parameter_seed import seed_opsi_parameter
    from app.seeder.parameter_seed import seed_parameter

    print("[1/5] Menyiapkan master parameter...")
    seed_parameter()
    print("[2/5] Menyiapkan opsi parameter...")
    seed_opsi_parameter()
    print("[3/5] Menyiapkan master diagnosis...")
    seed_diagnosa()
    print("[4/5] Menyiapkan master intervensi...")
    seed_intervensi()
    print("[5/5] Menyiapkan user dan rekam pasien dari dataset...")
    seed_dataset_pasien()


if __name__ == "__main__":
    seed_all_dataset_dependencies()
