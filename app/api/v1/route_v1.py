from app.api.v1.asuhan_route import router as asuhan_router
from app.api.v1.user_route import router as user_router
from app.api.v1.auth_route import router as auth_router
from app.api.v1.jadwal_route import router as jadwal_router
from app.api.v1.jadwal_tersedia_route import router as jadwal_tersedia_router
from app.api.v1.jadwal_libur_route import router as jadwal_libur_router
from app.api.v1.rekam_pasien_route import router as rekam_pasien_router
from app.api.v1.parameter_route import router as parameter_router
from app.api.v1.opsi_parameter_route import router as opsi_parameter_router
from app.api.v1.article_route import router as article_router
from app.api.v1.intervensi_route import router as intervensi_router
from app.api.v1.diagnosa_route import router as diagnosa_router


v1_router = [
    user_router,
    auth_router,
    jadwal_router,
    jadwal_tersedia_router,
    jadwal_libur_router,
    rekam_pasien_router,
    parameter_router,
    opsi_parameter_router,
    article_router,
    intervensi_router,
    diagnosa_router,
    asuhan_router
]