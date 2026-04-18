
from fastapi import APIRouter, Depends
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.rekam_pasien_schema import RekamPasienBase, RekamPasienCreate, RekamPasienUpdate
from app.utils.helpers.respons import APIResponse
from sqlalchemy.orm import Session
from app.api.v1.auth_route import get_db
from app.service.master.rekam_pasien_service import (
    delete_rekam_pasien_service,
    get_rekam_pasien_by_id_service,
    get_rekam_pasien_by_user_service,
    get_rekam_pasien_me_service,
    post_rekam_pasien_service,
    update_rekam_pasien_service,
)


router = APIRouter(prefix="/rekam-pasien", tags=["rekam-pasien"])

@router.get("/{pasien_id}", response_model=APIResponse[list[RekamPasienBase]], summary="Get Rekam Pasien by User ID")
def get_rekam_pasien_by_user(
    pasien_id: int,
    db: Session = Depends(get_db),
   _: None = Depends(require_role( RoleEnum.ahli_gizi, RoleEnum.tenaga_kesehatan))
):
    pasien_id = pasien_id
    rekam_pasien = get_rekam_pasien_by_user_service(db,pasien_id)
    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien
    )

@router.get("/", response_model=APIResponse[list[RekamPasienBase]], summary="Get Rekam Pasien by User ID")
def get_rekam_pasien_me(
   current_user = Depends(require_role(RoleEnum.pasien)),
   db: Session = Depends(get_db),
):
    pasien_id = current_user.user_id
    rekam_pasien = get_rekam_pasien_me_service(db,pasien_id)

    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien
    )

@router.get("/detail/{rekam_pasien_id}", response_model=APIResponse[RekamPasienBase], summary="Get Rekam Pasien by Rekam Pasien ID")
def get_rekam_pasien_by_id(
    rekam_pasien_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(RoleEnum.pasien, RoleEnum.ahli_gizi, RoleEnum.tenaga_kesehatan)),
):
    user_id = current_user.user_id
    role = current_user.role

    rekam_pasien = get_rekam_pasien_by_id_service(db,user_id,role,rekam_pasien_id)
    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien
    )

@router.post("/",response_model=APIResponse[RekamPasienBase], summary="Create Rekam Pasien")
def create_rekam_pasien(
    payload: RekamPasienCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi, RoleEnum.tenaga_kesehatan)),
):
    rekam_pasien = post_rekam_pasien_service(db,payload)
    return APIResponse(
        status_code=201,
        message="success",
        data=rekam_pasien
    )

@router.patch("/{rekam_pasien_id}", response_model=APIResponse[RekamPasienBase], summary="Update Rekam Pasien by Rekam Pasien ID")
def update_rekam_pasien_by_id(
    rekam_pasien_id: int,
    payload: RekamPasienUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi, RoleEnum.tenaga_kesehatan)),
):
    rekam_pasien = update_rekam_pasien_service(db,payload,rekam_pasien_id)
    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien
    )

@router.patch("/delete/{rekam_pasien_id}", response_model=APIResponse[RekamPasienBase], summary="Delete Rekam Pasien by Rekam Pasien ID")
def delete_rekam_pasien_by_id(
    rekam_pasien_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi, RoleEnum.tenaga_kesehatan)),
):
    rekam_pasien = delete_rekam_pasien_service(db, rekam_pasien_id)
    return APIResponse(
        status_code=200,
        message="success",
        data=rekam_pasien
    )

