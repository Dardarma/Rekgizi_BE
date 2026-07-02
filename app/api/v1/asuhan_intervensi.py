from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.api.v1.user_route import get_db
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.intervensi_schema import APIResponseIntervensi
from app.schemas.rekam_pasien_schema import APIRekamPasien, IntervensiRekamPasienRequest
from app.schemas.summary_schema import RekamPasienSummaryResponse
from app.service.Asuhan.intervensi_asuhan import get_rekam_pasien_summary, map_to_summary, prediksiIntervensi, putIntervensiPasienService, setujuiIntervensiService
from app.service.master.intervensi_service import get_intervensi_service
from app.utils.helpers.respons import APIResponse
from app.utils.dependencies.rekam_pasien import can_access_rekam_pasien_summary


router = APIRouter(prefix="/asuhan-intervensi", tags=["intervensi Asuhan"])

@router.get("/", response_model=APIResponseIntervensi, summary="Get intervensi by ID")
def get_intervensi(
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan))
):
    intervensi = get_intervensi_service(db)

    return APIResponse(
        status_code=200,
        message="success",
        data=intervensi
    )

@router.patch("/save_intervensi/{id_parameter_pasien}", response_model=APIRekamPasien, summary='patch rekam pasien intervensi')
def patchRekamPasienIntervesi(
  id_parameter_pasien : int,
  payload : IntervensiRekamPasienRequest,
  db: Session = Depends(get_db),
   _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan))  
):
    rekam_pasien = putIntervensiPasienService(db,id_parameter_pasien,payload)
    
    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien
    )
    
@router.get("/get_summary/{id_rekam_pasien}",response_model=RekamPasienSummaryResponse,summary="get summary rekam pasien")
def getRekamPasienSummary(
    id_rekam_pasien: int,
    db: Session = Depends(get_db),
    _: dict = Depends(can_access_rekam_pasien_summary)
):
    result = get_rekam_pasien_summary(db, id_rekam_pasien)
    summary = map_to_summary(result)

    return APIResponse(
        status_code=200,
        message="success",
        data=summary
    )

@router.get("/predict/{id_rekam_pasien}")
def getPredict(
    id_rekam_pasien,
    db:Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan))  
):
    result = prediksiIntervensi(db,id_rekam_pasien)
    
    return APIResponse(
        status_code=200,
        message="success",
        data= result
    )

@router.patch("/validasi/{id_rekam_pasien}", response_model=APIRekamPasien, summary='simpan dan validasi rekam pasien')
def setujuiIntervensi(
    id_rekam_pasien: int,
    payload: IntervensiRekamPasienRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    result = setujuiIntervensiService(db, id_rekam_pasien, payload)
    
    return APIResponse(
        status_code=200,
        message="success",
        data= result
    )
