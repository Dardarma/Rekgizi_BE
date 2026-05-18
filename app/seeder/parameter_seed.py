from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.parameter import Parameter, TipeInputEnum


def seed_parameter():
    db: Session = SessionLocal()

    try:
        data_parameter = [
            # ================= ANTROPOMETRI =================
            Parameter(nama="Tinggi badan", kategori="antropometri", tipe_input=TipeInputEnum.number, satuan="cm", important=True),
            Parameter(nama="Berat badan", kategori="antropometri", tipe_input=TipeInputEnum.number, satuan="kg", important=True),
            Parameter(nama="IMT", kategori="antropometri", tipe_input=TipeInputEnum.number, satuan="kg/m2", important=True),

            # ================= BIOKIMIA =================
            Parameter(nama="Creatinine", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="U/L", important=True),
            Parameter(nama="Ureum", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mg/dL", important=True),
            Parameter(nama="Asam Urat", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mg/dL",important=False),
            Parameter(nama="Natrium", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mEq/L", important=False),
            Parameter(nama="Kalium", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mEq/L", important=False),
            Parameter(nama="Glukosa Sewaktu", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mg/dL", important=False),
            Parameter(nama="Glukosa darah puasa", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="mg/dL", important=False),
            Parameter(nama="HgbA1c", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="%", important=False),
            Parameter(nama="Hemoglobin", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="g/dL", important=False),
            Parameter(nama="Albumin", kategori="biokimia", tipe_input=TipeInputEnum.number, satuan="g/dL", important=False),

            # ================= FISIK KLINIS =================
            Parameter(nama="Dispnea", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None, important=False),
            Parameter(nama="Anorexia", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None, important=False),
            Parameter(nama="Acites", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None, important=False),
            Parameter(nama="Nafsu makan menurun", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None, important=False),
            Parameter(nama="Mual", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None, important=False),
            Parameter(nama="Muntah", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None, important=False),
            Parameter(nama="Edema kaki", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None, important=False),
            Parameter(nama="Kulit mengelupas", kategori="fisik klinis", tipe_input=TipeInputEnum.boolean, satuan=None, important=False),
            Parameter(nama="Suhu", kategori="fisik klinis", tipe_input=TipeInputEnum.number, satuan="C", important=False),
            Parameter(nama="Tekanan darah", kategori="fisik klinis", tipe_input=TipeInputEnum.number, satuan="mmHg", important=True),

            # ================= RIWAYAT =================
            Parameter(nama="Jumlah Cairan melalui oral", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Jumlah Cairan dari makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Suplemen/cairan pengganti makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Jumlah makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Jenis makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Pola makan/snack", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Asupan protein bernilai biologis tinggi", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Asupan karbohidrat kompleks", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Asupan karbohidrat sederhana", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Penggunaan Resep Obat", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Komplementer/obat alternatif", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Kesukaan makanan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
            Parameter(nama="Pendidikan", kategori="riwayat", tipe_input=TipeInputEnum.select, satuan=None, important=False),
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