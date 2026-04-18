from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.user_route import get_db
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.diagnosa_schema import APIResponseDeleted, APIResponsediagnosa, APIResponsediagnosaId, diagnosaBasicInfo
from app.service.master.diagnosa_service import create_diagnosa_service, delete_diagnosa_service, edit_diagnosa_service, get_diagnosa_service
from app.utils.helpers.respons import APIResponse


router = APIRouter(prefix="/diagnosa", tags=["diagnosa"])

@router.get("/", response_model=APIResponsediagnosa, summary="Get Diagnosa")
def get_diagnosa(
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    diagnosa = get_diagnosa_service(db)
    
    return APIResponse(
        status_code=200,
        message="succes",
        data=diagnosa
    )
    
@router.post('/',response_model=APIResponsediagnosaId, summary="Create diagnosa")
def get_diagnosa(
    payload: diagnosaBasicInfo,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    diagnosa = create_diagnosa_service(db,payload)
    
    return APIResponse(
        status_code=201,
        message="Diagnosa created successfully",
        data=diagnosa
    )
    
@router.patch("/{diagnosa_id}", response_model=APIResponsediagnosaId, summary="Diagnosa edit ")
def edit_diagnosa(
    diagnosa_id: int,
    payload: diagnosaBasicInfo,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    diagnosa = edit_diagnosa_service(db, diagnosa_id, payload)
    
    return APIResponse(
        status_code=200,
        message="Diagnosa edited successfully",
        data=diagnosa
    )
    
@router.patch("/delete/{diagnosa_id}", response_model=APIResponseDeleted, summary="Diagnosa deleted ")
def edit_diagnosa(
    diagnosa_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    diagnosa = delete_diagnosa_service(db, diagnosa_id)
    
    return APIResponse(
        status_code=200,
        message="Diagnosa edited successfully",
        data=diagnosa
    )