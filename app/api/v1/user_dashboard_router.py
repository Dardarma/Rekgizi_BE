from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.user_route import get_db
from app.models.users import RoleEnum
from app.core.require_role import require_role
from app.utils.helpers.respons import APIResponse
from app.schemas.jadwal_schema import JadwalKonselingDashboardInfo
from app.service.dashboard.user_dashboard_service import get_jadwal_konsultasi_dashboard,get_intervensi_dashboard
from app.schemas.rekam_pasien_schema import RekamPasienDashboardUser

router = APIRouter(prefix="/user/dashboard", tags=["User Dashboard"])

@router.get("/jadwal", response_model=APIResponse[List[JadwalKonselingDashboardInfo]], summary="get jadwal konseling pasien")
def get_jadwal_user_dashboard(
    db: Session = Depends(get_db),
    ustate = Depends(require_role(RoleEnum.pasien)),
):
    user_id = ustate.user_id
    rekam_pasien = get_jadwal_konsultasi_dashboard(db, user_id)
    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien["data"]
    )

@router.get("/intervensi", response_model=APIResponse[List[RekamPasienDashboardUser]], summary="get rekam pasien")
def get_intervensi_user_dashboard(
    db: Session = Depends(get_db),
    ustate = Depends(require_role(RoleEnum.pasien)),
):  
    user_id = ustate.user_id
    rekam_pasien = get_intervensi_dashboard(db, user_id)
    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien["data"]
    )