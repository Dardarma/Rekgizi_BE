from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.user_route import get_db
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.parameter_schema import parameterBaseInfo, parameterCreate
from app.service.master.parameter_service import create_parameter_service, delete_parameter_service, get_parameter_by_id_service, get_parameter_service, updated_parameter_service
from app.utils.helpers.respons import APIResponse

router = APIRouter(prefix="/parameter", tags=["parameter"])

@router.get("/",response_model=APIResponse[List[parameterBaseInfo]], summary="Get all parameters")
def get_parameter(
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    parameter = get_parameter_service(db)

    return APIResponse(
        status_code=200,
        message="success",
        data=parameter
    )

@router.get("/{parameter_id}", response_model=APIResponse[parameterBaseInfo], summary="Get parameter by ID")
def get_parameter_by_id(
    parameter_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    parameter = get_parameter_by_id_service(db, parameter_id)

    return APIResponse(
        status_code=200,
        message="success",
        data=parameter
    )

@router.post("/", response_model=APIResponse[parameterBaseInfo], summary="Create new parameter")
def create_parameter(
    payload: parameterCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    parameter = create_parameter_service(db, payload)

    return APIResponse(
        status_code=201,
        message="Parameter created successfully",
        data=parameter
    )

@router.patch("/{parameter_id}", response_model=APIResponse[parameterBaseInfo], summary="Update parameter by ID")
def update_parameter(
    parameter_id: int,
    payload: parameterCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    parameter = updated_parameter_service(db, parameter_id, payload)

    return APIResponse(
        status_code=200,
        message="Parameter updated successfully",
        data=parameter
    )

@router.patch("/delete/{parameter_id}", response_model=APIResponse[parameterBaseInfo], summary="Delete parameter by ID")
def delete_parameter(
    parameter_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    parameter = delete_parameter_service(db, parameter_id)

    return APIResponse(
        status_code=200,
        message="Parameter deleted successfully",
        data=parameter
)