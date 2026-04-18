from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.parameter import Parameter, TipeInputEnum


def seed_parameter():
    db: Session = SessionLocal()

    try:
        data_parameter = [
            # ================= ANTROPOMETRI =================
            Parameter(nama="Tinggi badan", kategori="antropometri", tipe_input=TipeInputEnum.number, satuan="cm"),
            Parameter(nama="Berat badan", kategori="antropometri", tipe_input=TipeInputEnum.number, satuan="kg"),
            Parameter(nama="IMT", kategori="antropometri", tipe_input=TipeInputEnum.number, satuan="kg/m2"),

            # ================= BIOKIMIA =================
            Parameter(nama="Creatinine", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="U/L"),
            Parameter(nama="Ureum", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mg/dL"),
            Parameter(nama="Asam Urat", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mg/dL"),
            Parameter(nama="Natrium", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mEq/L"),
            Parameter(nama="Kalium", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mEq/L"),
            Parameter(nama="Glukosa Sewaktu", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mg/dL"),
            Parameter(nama="Glukosa darah puasa", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mg/dL"),
            Parameter(nama="HgbA1c", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="%"),
            Parameter(nama="Hemoglobin", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="g/dL"),
            Parameter(nama="Albumin", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="g/dL"),

            # ================= FISIK KLINIS =================
            Parameter(nama="Dispnea", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None),
            Parameter(nama="Anorexia", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None),
            Parameter(nama="Acites", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None),
            Parameter(nama="Nafsu makan menurun", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None),
            Parameter(nama="Mual", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None),
            Parameter(nama="Muntah", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None),
            Parameter(nama="Edema kaki", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None),
            Parameter(nama="Kulit mengelupas", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None),
            Parameter(nama="Suhu", kategori="fisik klinis", tipe_input=TipeInputEnum.number, satuan="C"),
            Parameter(nama="Tekanan darah", kategori="fisik klinis", tipe_input=TipeInputEnum.number, satuan="mmHg"),

            # ================= RIWAYAT =================
            Parameter(nama="Jumlah Cairan melalui oral", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Jumlah Cairan dari makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Suplemen/cairan pengganti makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Jumlah makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Jenis makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Pola makan/snack", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Asupan protein bernilai biologis tinggi", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Asupan karbohidrat kompleks", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Asupan karbohidrat sederhana", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Penggunaan Resep Obat", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Komplementer/obat alternatif", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Kesukaan makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
            Parameter(nama="Pendidikan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None),
        ]

        # OPTIONAL: biar gak double insert
        for item in data_parameter:
            existing = db.query(Parameter).filter_by(
                nama=item.nama,
                kategori=item.kategori
            ).first()

            if not existing:
                db.add(item)

        db.commit()

        print("Seeder parameter berhasil dijalankan ✅")

    except Exception as e:
        db.rollback()
        print("Seeder gagal:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_parameter()