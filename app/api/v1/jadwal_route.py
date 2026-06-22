from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.utils.helpers.respons import APIResponse
from app.core.require_role import require_role 
from app.api.v1.auth_route import get_db
from app.models.users import RoleEnum
from app.schemas.jadwal_schema import JadwalKonselingStatusCatatanUpdate, jadwalKonselingBasicInfo, jadwalKonselingCreate, jadwalKonselingUpdate, MetaPaginateSchemaJadwalKonseling
from app.service.jadwal_konseling.jadwal_service import create_jadwal_konseling_service, delete_jadwal_konseling_service, edit_jadwal_konseling_service, get_jadwal_konsultasi_by_id_service, get_jadwal_kosultasi_by_user as get_jadwal_by_user, ubah_status_dan_catatan_jadwal_konseling_service

router = APIRouter(prefix="/jadwal", tags=["jadwal"])

@router.get("/", response_model=MetaPaginateSchemaJadwalKonseling, summary="Get jadwal konsultasi berdasarkan user yang sedang login")
def get_jadwal_konsultasi(
    page: int = 1,
    limit: int = 10,
    state = Depends(require_role(RoleEnum.pasien, RoleEnum.ahli_gizi)),
    db: Session = Depends(get_db)
):
    user_id = state.user_id
    role = state.role
    jadwal_data = get_jadwal_by_user(db, user_id, role, page, limit)

    return MetaPaginateSchemaJadwalKonseling(
        status_code=200,
        message="success",
        data=jadwal_data["data"],
        current_page=jadwal_data["current_page"],
        limit=jadwal_data["limit"],
        total=jadwal_data["total"],
        total_pages=jadwal_data["total_pages"]
    )


@router.post("/", response_model=APIResponse[jadwalKonselingBasicInfo], summary="Create jadwal konsultasi")
def create_jadwal_konsultasi(
    payload: jadwalKonselingCreate,
    db: Session = Depends(get_db),
    state = Depends(require_role(RoleEnum.pasien))
):
    create_jadwal = create_jadwal_konseling_service(db, payload, state.user_id)

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

@router.patch("/status-catatan/{jadwal_id}", response_model=APIResponse[jadwalKonselingBasicInfo], summary="Update status dan catatan jadwal konsultasi by ID")
def update_status_dan_catatan_jadwal_konsultasi_by_id(
    jadwal_id: int,
    payload: JadwalKonselingStatusCatatanUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    updated_jadwal = ubah_status_dan_catatan_jadwal_konseling_service(db, jadwal_id, payload.status, payload.catatan)

    return APIResponse(
        status_code=200,
        message="Jadwal konsultasi status dan catatan updated successfully",
        data=updated_jadwal
    )

@router.delete("/{jadwal_id}", response_model=APIResponse[None], summary="Delete jadwal konsultasi by ID")
def delete_jadwal_konsultasi_by_id(
    jadwal_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.pasien, RoleEnum.ahli_gizi))
):
    delete_jadwal_konseling_service(db, jadwal_id)

    return APIResponse(
        status_code=200,
        message="Jadwal konsultasi deleted successfully",
        data=None
    )
