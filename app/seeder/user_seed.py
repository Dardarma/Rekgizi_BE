from sqlalchemy.orm import Session
from datetime import date

from app.core.database import SessionLocal
from app.models.users import User
from app.core.security import hash_password


def seed_users():
    db: Session = SessionLocal()

    user_data = [
        {
            "nama": "Admin",
            "email": "admin@example.com",
            "pass_hash": hash_password("password"),
            "role": "admin",
            "jenis_kelamin": "pria",
            "alamat": {
                "desa": "Contoh Desa",
                "kecamatan": "Jakarta",
                "kota": "DKI Jakarta",
                "provinsi": "DKI Jakarta",
                "lengkap": "Contoh Desa, Jakarta, DKI Jakarta 12345"
            },
            "tanggal_lahir": date(1990, 1, 1)
        },
        {
            "nama": "User",
            "email": "user@example.com",
            "pass_hash": hash_password("password"),
            "role": "pasien",
            "jenis_kelamin": "pria",
            "alamat": {
                "desa": "Contoh Desa",
                "kecamatan": "Jakarta",
                "kota": "DKI Jakarta",
                "provinsi": "DKI Jakarta",
                "lengkap": "Contoh Desa, Jakarta, DKI Jakarta 12345"
            },
            "tanggal_lahir": date(1990, 1, 1)
        },
        {
            "nama": "Ahli Gizi",
            "email": "ahligizi@example.com",
            "pass_hash": hash_password("password"),
            "role": "ahli_gizi",
            "jenis_kelamin": "pria",
            "alamat": {
                "desa": "Contoh Desa",
                "kecamatan": "Jakarta",
                "kota": "DKI Jakarta",
                "provinsi": "DKI Jakarta",
                "lengkap": "Contoh Desa, Jakarta, DKI Jakarta 12345"
            },
            "tanggal_lahir": date(1990, 1, 1)
        }
    ]

    for user in user_data:
        existing_user = db.query(User).filter(User.email == user["email"]).first()

        if not existing_user:
            new_user = User(**user)
            db.add(new_user)

    db.commit()
    db.close()


if __name__ == "__main__":
    seed_users()