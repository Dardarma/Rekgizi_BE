"""Model package initialization loading all ORM models."""

from app.models.article import Article
from app.models.diagnosa import Diagnosa
from app.models.diagnosa_pasien import DiagnosaPasien
from app.models.intevensi import Intervensi
from app.models.jadwal_konseling import JadwalKonseling
from app.models.jadwal_libur import JadwalLibur
from app.models.jadwal_tersedia import JadwalTersedia
from app.models.opsi_parameter import OpsiParameter
from app.models.parameter import Parameter
from app.models.rekam_pasien import RekamPasien
from app.models.rekam_pasien_parameter import RekamPasienParameter
from app.models.users import User

__all__ = [
    "Article",
    "Diagnosa",
    "DiagnosaPasien",
    "Intervensi",
    "JadwalKonseling",
    "JadwalLibur",
    "JadwalTersedia",
    "OpsiParameter",
    "Parameter",
    "RekamPasien",
    "RekamPasienParameter",
    "User",
]
