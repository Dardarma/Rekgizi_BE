from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.v1.user_route import get_db
from app.models.users import RoleEnum
from app.core.require_role import require_role
from app.utils.helpers.respons import APIResponse
from app.service.dashboard.ahli_gizi_dashboard_service import getInformationYearly, getPersebaranKasusService, getRekamPasienDashboardService, getRekamPasienPerPekan, getUsiaPerTahunService
from app.schemas.dashboard_schema import dashboardAhliGiziBaseInfo, rekamPaseinDashboard


router = APIRouter(prefix="/ahligizi/dashboard", tags=["Ahli Gizi Dashboard"])

@router.get(
    "/total",
    response_model=APIResponse[dashboardAhliGiziBaseInfo],
    summary="get total base on year"
)
def get_total_dashboard(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    ustate = Depends(require_role(RoleEnum.ahli_gizi))
):
    information = getInformationYearly(db, ustate.user_id, year, month)

    return APIResponse(
        status_code=200,
        message="success",
        data=information
    )

@router.get(
    "/rekam_pasien",
    summary="get rekam pasien "
) 
def get_rekam_pasien(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    rekam_pasien = getRekamPasienDashboardService(db, year, month)
    
    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien
    )

@router.get(
    '/persebaran_kasus',
    summary= "persebaran kasus sebulan"
)
def getPersebaranKasus(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    chart_kasus = getPersebaranKasusService(db, year, month)

    return APIResponse(
         status_code = "200",
         message = "success",
         data=chart_kasus
    )
       
@router.get(
    '/persebaran_minggu',
    summary= "persebaran kasus mingguan"
)
def getPersebaranMingguan(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    
    chart_mingguan = getRekamPasienPerPekan(db, year, month)
    
    return APIResponse(
        status_code = "200",
        message = "success",
        data = chart_mingguan
    )
      
@router.get(
    '/persebaran_usia',
    summary="Persebaran usia dari "
)  
def getUsiaPerTahun(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    chart_usia = getUsiaPerTahunService(db, year, month)
    
    return APIResponse(
        status_code = "200",
        message = "success",
        data = chart_usia
    )
