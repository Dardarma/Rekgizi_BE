from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.utils.helpers.respons import APIResponse
from app.core.require_role import require_role 
from app.api.v1.auth_route import get_db
from app.models.users import RoleEnum
from app.schemas.jadwal_schema import JadwalKonselingStatus, jadwalKonselingBasicInfo, jadwalKonselingCreate, jadwalKonselingUbahCatatan, jadwalKonselingUpdate
from app.service.jadwal_konseling.jadwal_service import create_jadwal_konseling_service, delete_jadwal_konseling_service, edit_jadwal_konseling_service, get_jadwal_konsultasi_by_id_service, get_jadwal_kosultasi_by_user as get_jadwal_by_user, ubah_catatan_jadwal_konseling_service, ubah_status_jadwal_konseling_service

router = APIRouter(prefix="/jadwal", tags=["jadwal"])

@router.get("/", response_model=APIResponse[List[jadwalKonselingBasicInfo]], summary="Get jadwal konsultasi berdasarkan user yang sedang login")
def get_jadwal_konsultasi(
    state = Depends(require_role(RoleEnum.pasien, RoleEnum.ahli_gizi)),
    db: Session = Depends(get_db)
):
    user_id = state.user_id
    role = state.role
    jadwal = get_jadwal_by_user(db, user_id, role)

    return APIResponse(
        status_code=200,
        message="success",
        data= jadwal
    )

@router.post("/", response_model=APIResponse[jadwalKonselingBasicInfo], summary="Create jadwal konsultasi")
def create_jadwal_konsultasi(
    payload: jadwalKonselingCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.pasien))
):
    create_jadwal = create_jadwal_konseling_service(db, payload)

    return APIResponse(
        status_code=201,
        message="Jadwal konsultasi created successfully",
        data=create_jadwal
    )

@router.get("/{jadwal_id}", response_model=APIResponse[jadwalKonselingBasicInfo], summary="Get jadwal konsultasi by ID")
def get_jadwal_konsultasi_by_id(
    jadwal_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.pasien, RoleEnum.ahli_gizi))
):
    jadwal = get_jadwal_konsultasi_by_id_service(db, jadwal_id)

    if not jadwal:
        raise HTTPException(status_code=404, detail="Jadwal konsultasi not found")

    return APIResponse(
        status_code=200,
        message="success",
        data= jadwal
    )

@router.patch("/{jadwal_id}", response_model=APIResponse[jadwalKonselingBasicInfo], summary="Update jadwal konsultasi by ID")
def update_jadwal_konsultasi_by_id(
    jadwal_id: int,
    payload: jadwalKonselingUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    updated_jadwal = edit_jadwal_konseling_service(db, jadwal_id, payload)

    return APIResponse(
        status_code=200,
        message="Jadwal konsultasi updated successfully",
        data=updated_jadwal
    )

@router.patch("/status/{jadwal_id}", response_model=APIResponse[jadwalKonselingBasicInfo], summary="Update status jadwal konsultasi by ID")
def update_status_jadwal_konsultasi_by_id(
    jadwal_id: int,
    payload: JadwalKonselingStatus,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    updated_jadwal = ubah_status_jadwal_konseling_service(db, jadwal_id, payload.status)

    return APIResponse(
        status_code=200,
        message="Jadwal konsultasi status updated successfully",
        data=updated_jadwal
    )

@router.patch("/catatan/{jadwal_id}", response_model=APIResponse[jadwalKonselingBasicInfo], summary="Update catatan jadwal konsultasi by ID")
def update_catatan_jadwal_konsultasi_by_id(
    jadwal_id: int,
    payload: jadwalKonselingUbahCatatan,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    updated_jadwal = ubah_catatan_jadwal_konseling_service(db, jadwal_id, payload.catatan)

    return APIResponse(
        status_code=200,
        message="Jadwal konsultasi catatan updated successfully",
        data=updated_jadwal
    )

@router.patch("/{jadwal_id}", response_model=APIResponse[None], summary="Delete jadwal konsultasi by ID")
def delete_jadwal_konsultasi_by_id(
    jadwal_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    delete_jadwal_konseling_service(db, jadwal_id)

    return APIResponse(
        status_code=200,
        message="Jadwal konsultasi deleted successfully",
        data=None
    )
