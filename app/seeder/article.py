from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.article import Article


def seed_article():
    db: Session = SessionLocal()

    try:
        data_articles = [
            {
                "user_id": 1,
                "judul": "Pengenalan Penyakit Ginjal Kronis (PGK)",
                "konten": "Penyakit Ginjal Kronis (PGK) adalah kondisi penurunan fungsi ginjal secara bertahap dalam jangka waktu lama. PGK sering tidak menunjukkan gejala di tahap awal sehingga penting untuk melakukan pemeriksaan rutin.",
                "is_published": True
            },
            {
                "user_id": 1,
                "judul": "Gejala Awal PGK yang Sering Diabaikan",
                "konten": "Gejala awal PGK meliputi kelelahan, pembengkakan pada kaki, perubahan frekuensi buang air kecil, dan tekanan darah tinggi. Banyak pasien tidak menyadari kondisi ini hingga memasuki tahap lanjut.",
                "is_published": True
            },
            {
                "user_id": 2,
                "judul": "Pola Makan untuk Pasien PGK",
                "konten": "Pasien PGK disarankan mengurangi asupan natrium, fosfor, dan protein berlebih. Konsumsi makanan segar seperti sayuran rendah kalium sangat dianjurkan untuk menjaga fungsi ginjal.",
                "is_published": True
            },
            {
                "user_id": 2,
                "judul": "Peran Dialisis pada PGK Stadium Akhir",
                "konten": "Dialisis diperlukan ketika fungsi ginjal sudah sangat menurun. Proses ini membantu menyaring limbah dan cairan berlebih dari tubuh yang tidak dapat lagi dilakukan oleh ginjal.",
                "is_published": True
            },
            {
                "user_id": 3,
                "judul": "Pencegahan Penyakit Ginjal Kronis",
                "konten": "Pencegahan PGK dapat dilakukan dengan menjaga tekanan darah, mengontrol gula darah, menghindari konsumsi obat sembarangan, dan menerapkan gaya hidup sehat.",
                "is_published": False
            },
            {
                "user_id": 3,
                "judul": "Hubungan Diabetes dengan PGK",
                "konten": "Diabetes merupakan salah satu penyebab utama PGK. Kadar gula darah yang tidak terkontrol dapat merusak pembuluh darah kecil di ginjal.",
                "is_published": True
            },
            {
                "user_id": 1,
                "judul": "Pentingnya Pemeriksaan Rutin Ginjal",
                "konten": "Pemeriksaan rutin seperti cek kreatinin dan laju filtrasi glomerulus (GFR) penting untuk mendeteksi PGK sejak dini.",
                "is_published": False
            },
            {
                "user_id": 2,
                "judul": "Komplikasi yang Dapat Terjadi pada PGK",
                "konten": "PGK dapat menyebabkan komplikasi seperti anemia, gangguan tulang, hingga penyakit kardiovaskular jika tidak ditangani dengan baik.",
                "is_published": True
            }
        ]

        for item in data_articles:
            existing = db.query(Article).filter_by(judul=item["judul"]).first()

            if not existing:
                db.add(Article(**item))

        db.commit()
        print("Seeder article PGK berhasil dijalankan ✅")

    except Exception as e:
        db.rollback()
        print("Seeder gagal:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_article()