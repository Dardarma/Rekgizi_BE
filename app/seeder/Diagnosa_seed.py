from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.diagnosa import Diagnosa


def seed_diagnosa():
    db: Session = SessionLocal()

    try:
        data_diagnosa = [
            {"kode": "NI-2.1", "diagnosa": "Kekurangan intake makanan dan minuman oral"},
            {"kode": "NI-2.2", "diagnosa": "Kelebihan intake makanan dan minuman oral"},
            {"kode": "NI-2.5", "diagnosa": "Ketidaksesuaian asupan enteral"},
            {"kode": "NI-2.9", "diagnosa": "Penerimaan makan terbatas"},
            {"kode": "NI-3.1", "diagnosa": "Asupan cairan indequat"},
            {"kode": "NI-3.2", "diagnosa": "Kelebihan asupan cairan"},
            {"kode": "NI-5.1", "diagnosa": "Peningkatan kebutuhan zat gizi"},
            {"kode": "NI-5.2", "diagnosa": "Malnutrition"},
            {"kode": "NI-5.3", "diagnosa": "Kekurangan asupan energi protein"},
            {"kode": "NI-5.4", "diagnosa": "Penurunan kebutuhan gizi tertentu"},

            {"kode": "NC-1.1", "diagnosa": "Kesulitan menelan"},
            {"kode": "NC-1.2", "diagnosa": "Kesulitan mengunyah"},
            {"kode": "NC-1.4", "diagnosa": "Perubahan fungsi gastrointestinal"},
            {"kode": "NC-2.1", "diagnosa": "Perubahan nilai laborat terkait gizi"},
            {"kode": "NC-3.1", "diagnosa": "Berat badan kurang"},
            {"kode": "NC-3.2", "diagnosa": "Penurunan berat badan yang tidak diharapkan"},
            {"kode": "NC-3.3", "diagnosa": "Berat badan berlebih"},
            {"kode": "NC-3.4", "diagnosa": "Kelebihan berat badan yang tidak diharapkan"},

            {"kode": "NB-1.1", "diagnosa": "Pengetahuan yang kurang terkait dengan pangan dan gizi"},
            {"kode": "NB-1.2", "diagnosa": "Kepercayaan yang salah tentang pangan dan gizi"},
            {"kode": "NB-1.4", "diagnosa": "Kurangnya memonitor diri sendiri"},
            {"kode": "NB-1.5", "diagnosa": "Kekeliruan pola makan"},
            {"kode": "NB-3.1", "diagnosa": "Asupan makanan yang tidak aman"},
        ]

        for item in data_diagnosa:
            existing = db.query(Diagnosa).filter_by(kode=item["kode"]).first()

            if not existing:
                db.add(Diagnosa(**item))

        db.commit()
        print("Seeder diagnosa berhasil dijalankan ✅")

    except Exception as e:
        db.rollback()
        print("Seeder gagal:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_diagnosa()