from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.user_route import get_db
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.intervensi_schema import APIResponseIntervensi, APIResponseIntervensiDeleted, APIResponseIntervensiId, IntervensiBasicInfo
from app.service.master.intervensi_service import create_intervensi_service, delete_intervensi_service, edit_intervensi_service, get_intervensi_by_id_service, get_intervensi_service
from app.utils.helpers.respons import APIResponse

router = APIRouter(prefix="/intervensi", tags=["intervensi"])

@router.get("/", response_model=APIResponseIntervensi, summary="Get intervensi by ID")
def get_intervensi(
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    intervensi = get_intervensi_service(db)

    return APIResponse(
        status_code=200,
        message="success",
        data=intervensi
    )
    
@router.get("/{intervensi_id}", response_model=APIResponseIntervensiId, summary="Get intervensi by ID")
def get_intervensi_by_id(
    intervensi_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    intervensi = get_intervensi_by_id_service(db, intervensi_id)

    return APIResponse(
        status_code=200,
        message="success",
        data=intervensi
    )
    
@router.post("/", response_model=APIResponseIntervensiId, summary="Create intervensi")
def create_intervensi(
    payload: IntervensiBasicInfo,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    intervensi = create_intervensi_service(db, payload)

    return APIResponse(
        status_code=201,
        message="Intervensi created successfully",
        data=intervensi
    )
    
@router.patch("/{intervensi_id}", response_model=APIResponseIntervensiId, summary="Edit intervensi by ID")
def edit_intervensi(
    intervensi_id: int,
    payload: IntervensiBasicInfo,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    intervensi = edit_intervensi_service(db, intervensi_id, payload)

    return APIResponse(
        status_code=200,
        message="Intervensi updated successfully",
        data=intervensi
    )
    
@router.patch("/delete/{intervensi_id}", response_model=APIResponseIntervensiDeleted, summary="Delete intervensi by ID")
def delete_intervensi(
    intervensi_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    intervensi = delete_intervensi_service(db, intervensi_id)
    
    return APIResponse(
        status_code=200,
        message="Intervensi deleted successfully",
        data=intervensi
    )
    