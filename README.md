# Rekgizi Backend

Backend Rekgizi menggunakan FastAPI, SQLAlchemy, dan PostgreSQL.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python migrate.py
python -m uvicorn app.main:app --reload
```

Untuk mengisi master parameter, opsi, diagnosis, serta 20 pasien beserta rekam medisnya dalam satu langkah:

```powershell
python -m app.seeder.dataset_pasien_seed
```

Seeder membuat akun `pasien.dataset.001@example.com` sampai `pasien.dataset.020@example.com` dengan password development `password`. Saat dijalankan ulang, akun lama berdomain `@rekgizi.test` otomatis diperbarui tanpa membuat user duplikat. Tanggal lahir dibuat bervariasi sesuai kelompok usia dan jenis kelamin dibuat bergantian karena kedua nilai tersebut tidak tersedia di CSV.

Konfigurasi environment, koneksi database, seeder, dan daftar library lengkap tersedia di [dokumentasi setup](../README.md).
