from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.user_route import get_db
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.parameter_opsi_schema import APIResponseOpsiParameter, APIResponseOpsiParameterID, OpsiParameterCreate, OpsiParameterUpdate
from app.service.master.opsi_parameter_service import delete_opsi_parameter_service, get_opsi_parameter_by_id_service, get_opsi_parameter_by_param_service, post_opsi_parameter_service, updated_opsi_parameter_service
from app.utils.helpers.respons import APIResponse

router = APIRouter(prefix="/opsi-parameter", tags=["opsi-parameter"])

@router.get("/{parameter_id}", response_model=APIResponseOpsiParameter, summary="Get opsi parameters by parameter ID")
def get_opsi_parameters_by_parameter_id(
    parameter_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    opsi_parameters = get_opsi_parameter_by_param_service(db, parameter_id)

    return APIResponse(
        status_code=200,
        message="success",
        data=opsi_parameters
    )

@router.get("/detail/{opsi_parameter_id}", response_model=APIResponseOpsiParameterID, summary="Get opsi parameter by ID")
def get_opsi_parameter_by_id(
    opsi_parameter_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    opsi_parameter = get_opsi_parameter_by_id_service(db, opsi_parameter_id)

    return APIResponse(
        status_code=200,
        message="success",
        data=opsi_parameter
    )

@router.post("/", response_model=APIResponseOpsiParameterID, summary="Create new opsi parameter")
def create_opsi_parameter(
    payload: OpsiParameterCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    opsi_parameter = post_opsi_parameter_service(db, payload)

    return APIResponse(
        status_code=201,
        message="Opsi Parameter created successfully",
        data=opsi_parameter
    )

@router.patch("/{opsi_parameter_id}", response_model=APIResponseOpsiParameterID, summary="Update opsi parameter by ID")
def update_opsi_parameter(
    opsi_parameter_id: int,
    payload: OpsiParameterUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    opsi_parameter = updated_opsi_parameter_service(db, opsi_parameter_id, payload)

    return APIResponse(
        status_code=200,
        message="Opsi Parameter updated successfully",
        data=opsi_parameter
    )

@router.patch("/delete/{opsi_parameter_id}", response_model=APIResponseOpsiParameterID, summary="Delete opsi parameter by ID")
def delete_opsi_parameter(
    opsi_parameter_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    opsi_parameter = delete_opsi_parameter_service(db, opsi_parameter_id)

    return APIResponse(
        status_code=200,
        message="Opsi Parameter deleted successfully",
        data=opsi_parameter
    )

