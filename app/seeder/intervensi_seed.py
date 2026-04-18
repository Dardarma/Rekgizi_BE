from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.intevensi import Intervensi


def seed_intervensi():
    db: Session = SessionLocal()

    try:
        data_intervensi = [
            {
                "jenis_diet": "Diet Ginjal Protein 30 g",
                "tujuan": "Pembatasan jumlah protein, natrium, kalium, fosfor dan cairan",
                "prinsip": """1. Mempertahankan status gizi yang optimal.
2. Mengurangi dan mencegah gejala uremia.
3. Mengurangi progresivitas gagal ginjal dan memperlambat turunnya laju filtrasi glomerulus.""",
                "edukasi": """Rencana Diet:
Protein 30 g, Energi 1729 kal, Lemak 57 g, Karbohidrat 263 g.

Intervensi Diet:
Batasi protein ±30 gram/hari (sekitar 0,6 g/kg BB/hari jika BB 50 kg).
Utamakan protein bernilai biologis tinggi seperti telur, susu, ayam tanpa kulit, ikan.
Kalori harus tetap cukup 30–35 kkal/kg BB agar tubuh tidak memecah otot.
Batasi natrium (garam) <1 sendok teh/hari untuk mencegah bengkak dan hipertensi.
Kontrol kalium dan fosfor jika kadar darah tinggi.
Cairan diatur bila ada edema atau gagal ginjal lanjut sesuai rekomendasi dokter.""",
                "protein": 30,
                "energi": 1729,
                "karbohidrat": 263,
            },
            {
                "jenis_diet": "Diet Ginjal Protein 35 g",
                "tujuan": "Pembatasan jumlah protein, natrium, kalium, fosfor dan cairan",
                "prinsip": """1. Mempertahankan status gizi yang optimal.
2. Mengurangi dan mencegah gejala uremia.
3. Mengurangi progresivitas gagal ginjal dan memperlambat turunnya laju filtrasi glomerulus.""",
                "edukasi": """Rencana Diet:
Protein 35 g, Energi 2086 kal, Lemak 70 g, Karbohidrat 327 g.

Intervensi Edukasi:
Batasi protein ±35 gram/hari (≈0,6–0,8 g/kg BB/hari jika BB 50 kg).
Utamakan protein bernilai biologis tinggi seperti telur, ikan, ayam tanpa kulit, susu rendah protein.
Kalori harus cukup 30–35 kkal/kg BB/hari agar tubuh tidak memecah otot.
Batasi natrium 2 gram/hari (≈5 gram garam dapur).
Kontrol kalium dan fosfor bila kadar darah tinggi.
Cairan diatur bila edema sesuai rekomendasi dokter.
Cara memasak: rebus, kukus, tumis ringan, panggang. Hindari gorengan dan makanan tinggi garam.""",
                "protein": 35,
                "energi": 2086,
                "karbohidrat": 327,
            },
            {
                "jenis_diet": "Diet Ginjal Protein 60 g",
                "tujuan": "Meningkatkan asupan energi dan protein berkualitas tinggi, membatasi natrium, kalium, dan fosfat, serta mengontrol cairan",
                "prinsip": """1. Memberikan protein yang cukup untuk mengganti asam amino esensial dan nitrogen yang hilang dalam dialisat.
2. Mencegah penimbunan hasil sisa metabolisme.
3. Mempertahankan status gizi normal.""",
                "edukasi": """Rencana Diet:
Protein 62 g, Energi 2002 kal, Lemak 67 g, Karbohidrat 290 g.

Intervensi Edukasi:
Tingkatkan kebutuhan protein ±60 gram/hari (1,0–1,2 g/kg BB/hari).
Utamakan protein bernilai biologis tinggi seperti telur, ikan, ayam tanpa kulit, daging tanpa lemak, susu renal.
Kalori harus tetap cukup 30–35 kkal/kg BB/hari untuk mencegah katabolisme otot.
Batasi natrium 2 gram/hari (≈5 gram garam dapur).
Kontrol kalium dan fosfor sesuai hasil laboratorium.
Batasi cairan: urin 24 jam + 500–700 ml.
Cara memasak: rebus, kukus, panggang, tumis ringan. Hindari makanan olahan tinggi garam.""",
                "protein": 60,
                "energi": 2002,
                "karbohidrat": 290,
            },
            {
                "jenis_diet": "Diet Ginjal Protein 65 g",
                "tujuan": "Meningkatkan asupan energi dan protein berkualitas tinggi, membatasi natrium, kalium, dan fosfat, serta mengontrol cairan",
                "prinsip": """1. Memberikan protein yang cukup untuk mengganti kehilangan saat dialisis.
2. Mencegah penimbunan metabolisme.
3. Mempertahankan status gizi normal.""",
                "edukasi": """Rencana Diet:
Protein 67 g, Energi 2039 kal, Lemak 68 g, Karbohidrat 293 g.

Intervensi Edukasi:
Tingkatkan protein ±65 gram/hari (≈1,1–1,3 g/kg BB/hari).
Utamakan protein biologis tinggi seperti telur, ikan, ayam/daging tanpa lemak, susu renal.
Kalori harus cukup 30–35 kkal/kg BB/hari.
Batasi natrium 2 gram/hari.
Kontrol kalium dan fosfor bila tinggi.
Batasi cairan sesuai anjuran dokter.
Cara memasak: rebus, kukus, panggang, tumis ringan.""",
                "protein": 65,
                "energi": 2039,
                "karbohidrat": 293,
            },
            {
                "jenis_diet": "Diet Ginjal Protein 70 g",
                "tujuan": "Meningkatkan asupan energi dan protein berkualitas tinggi, membatasi natrium, kalium, dan fosfat, serta mengontrol cairan",
                "prinsip": """1. Memberikan protein yang cukup untuk mengganti kehilangan saat dialisis.
2. Mencegah penimbunan metabolisme.
3. Mempertahankan status gizi normal.""",
                "edukasi": """Rencana Diet:
Protein 72 g, Energi 2039 kal, Lemak 72 g, Karbohidrat 301 g.

Intervensi Edukasi:
Tingkatkan protein ±70 gram/hari (≈1,2–1,4 g/kg BB/hari).
Utamakan protein biologis tinggi seperti telur, ikan, ayam/daging tanpa lemak, susu renal.
Kalori harus cukup 30–35 kkal/kg BB/hari.
Batasi natrium 2 gram/hari.
Kontrol kalium dan fosfor sesuai hasil lab.
Batasi cairan: urin 24 jam + 500–700 ml.
Cara memasak: rebus, kukus, panggang, tumis ringan. Hindari makanan tinggi garam.""",
                "protein": 70,
                "energi": 2039,
                "karbohidrat": 301,
            },
        ]

        for item in data_intervensi:
            existing = (
                db.query(Intervensi)
                .filter_by(jenis_diet=item["jenis_diet"])
                .first()
            )

            if not existing:
                db.add(Intervensi(**item))

        db.commit()
        print("Seeder intervensi berhasil dijalankan ✅")

    except Exception as e:
        db.rollback()
        print("Seeder gagal:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_intervensi()