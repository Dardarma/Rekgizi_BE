from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.diagnosa_schema import APIResponsediagnosa
from app.schemas.parameter_schema import ParameterWithOpsi
from app.schemas.rekam_pasien_parameter_schema import rekamPasienParameterRequest, rekamPasienParmeterResponse
from app.schemas.userSchema import UserBasicInfo, UserSearchRequest, userResponseAPI
from app.service.Asuhan.inputAsuhan import get_parameter_input_service, getRekamPasienParameterService, saveParameterPasien
from app.service.master.diagnosa_service import get_diagnosa_service
from app.service.user_service import get_all_users, get_user_by_id
from app.utils.helpers.respons import APIResponse



router = APIRouter(prefix="/asuhan", tags=["asuhan"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/search", response_model=APIResponse[userResponseAPI], summary="Search Asuhan user")
def get_asuhan_search(
    db: Session = Depends(get_db),
    user_request_schema: UserSearchRequest = Depends(),
    only_pasien: bool = True,
    _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan))
):
    user = get_all_users(db,user_request_schema,only_pasien)
    
    return APIResponse(
        status_code=200,
        message="success",
        data = user
    )
    

@router.get("/biodata/{user_id}",response_model=APIResponse[UserBasicInfo], summary="get user information")
def get_biodata(
    user_id:int,
    db: Session = Depends(get_db),
     _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan))
):
    user = get_user_by_id(user_id, db)
    
    return APIResponse(
		status_code=200, 
		message="Success", 
		data=user
	)
    
@router.get("/getInput", response_model=APIResponse[List[ParameterWithOpsi]], summary="get semua input dari parameter")
def get_parameter_input(
    db: Session = Depends(get_db),
     _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan))
):
    paramater = get_parameter_input_service(db)
    
    return APIResponse(
        status_code=200, 
        message="Success",
        data= paramater
    )
    
@router.get("/getdiagnosa", response_model=APIResponsediagnosa, summary="Get Diagnosa")
def get_diagnosa(
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan))
):
    diagnosa = get_diagnosa_service(db)
    
    return APIResponse(
        status_code=200,
        message="succes",
        data=diagnosa
    )
    
@router.post("/create/rekam-pasien-parameter",response_model=rekamPasienParmeterResponse, summary="post parameter")
def postRekamPasienParameter(
    payload: rekamPasienParameterRequest,
    db:Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan))
):
    rekam_pasien_parameter = saveParameterPasien(db,payload.rekam_pasien_id,payload.data)

    return APIResponse(
        status_code=200,
        message="succes",
        data=rekam_pasien_parameter
    )
    
@router.get("/rekam-pasien-parameter/{rekam_pasien_id}", response_model=rekamPasienParmeterResponse, summary="get parameter by rekam pasien id")
def getRekamPasienParameter(
    rekam_pasien_id: int,
    db:Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi,RoleEnum.tenaga_kesehatan)),
):
    rekam_pasien_parameter = getRekamPasienParameterService(db,rekam_pasien_id)
    
    return APIResponse(
        status_code=200,
        message="succes",
        data=rekam_pasien_parameter
    )

