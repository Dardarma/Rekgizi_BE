from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.parameter import Parameter
from app.models.opsi_parameter import OpsiParameter


def seed_opsi_parameter():
    db: Session = SessionLocal()

    try:
        data_opsi = {
            "Jumlah Cairan melalui oral": ["Kurang", "Sesuai", "Lebih"],
            "Jumlah Cairan dari makanan": ["Kurang", "Sesuai", "Lebih"],
            "Suplemen/cairan pengganti makanan": ["Kurang", "Sesuai", "Lebih"],
            "Jumlah makanan": ["Kurang", "Sesuai", "Lebih"],

            "Jenis makanan": ["Sesuai", "Tidak sesuai"],
            "Pola makan/snack": ["Sesuai", "Tidak sesuai"],
            "Asupan protein bernilai biologis tinggi": ["Sesuai", "Tidak sesuai"],
            "Asupan karbohidrat kompleks": ["Sesuai", "Tidak sesuai"],
            "Asupan karbohidrat sederhana": ["Sesuai", "Tidak sesuai"],
            "Kesukaan makanan": ["Sesuai", "Tidak sesuai"],

            "Penggunaan Resep Obat": ["Tidak pernah", "Kadang", "Sering", "Sangat sering"],
            "Komplementer/obat alternatif": ["Tidak pernah", "Kadang", "Sering", "Sangat sering"],

            "Pendidikan": ["Tidak sekolah", "SD", "SMP", "SMA", "Perguruan Tinggi"],
        }

        for nama_param, opsi_list in data_opsi.items():
            # cari parameter berdasarkan nama
            parameter = db.query(Parameter).filter_by(nama=nama_param).first()

            if not parameter:
                print(f"Parameter tidak ditemukan: {nama_param}")
                continue

            for opsi in opsi_list:
                # cek biar gak duplicate
                existing = db.query(OpsiParameter).filter_by(
                    parameter_id=parameter.id,
                    jawaban=opsi
                ).first()

                if not existing:
                    db.add(OpsiParameter(
                        parameter_id=parameter.id,
                        jawaban=opsi
                    ))

        db.commit()
        print("Seeder opsi parameter berhasil dijalankan ✅")

    except Exception as e:
        db.rollback()
        print("Seeder gagal:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_opsi_parameter()