from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.utils.helpers.respons import APIResponse
from app.core.require_role import require_role 
from app.api.v1.auth_route import get_db
from app.models.users import RoleEnum
from app.schemas.jadwal_libur import JadwalLiburBasicInfo, JadwalLiburCreate, JadwalLiburDeleted
from app.service.jadwal_konseling.jadwal_libur_service import (
    create_jadwal_libur_service,
    get_jadwal_libur_by_id_service,
    get_jadwal_libur_service,
    delete_jadwal_libur_service
)

router = APIRouter(prefix="/jadwal_libur", tags=["jadwal-libur"])

@router.get("/", response_model=APIResponse[List[JadwalLiburBasicInfo]], summary="Get jadwal libur")
def get_jadwal_libur(
    state = Depends(require_role(RoleEnum.ahli_gizi)),
    db: Session = Depends(get_db)
): 
    user_id = state.user_id
    jadwal_libur = get_jadwal_libur_service(db, user_id)

    if not jadwal_libur:
        raise HTTPException(status_code=404, detail="Jadwal libur not found")
    
    return APIResponse(
        status_code=200,
        message="success",
        data= jadwal_libur
    )


@router.post("/", response_model=APIResponse[JadwalLiburBasicInfo], summary="Create jadwal libur")
def create_jadwal_libur(
    payload: JadwalLiburCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    create_jadwal_libur = create_jadwal_libur_service(db,payload)

    return APIResponse(
        status_code=201,
        message="Jadwal libur created successfully",
        data=create_jadwal_libur
    )

@router.get("/{jadwal_libur_id}", response_model=APIResponse[JadwalLiburBasicInfo], summary="Get jadwal libur by ID")
def get_jadwal_libur_by_id(
    jadwal_libur_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    jadwal_libur = get_jadwal_libur_by_id_service(db, jadwal_libur_id=jadwal_libur_id)

    if not jadwal_libur:
        raise HTTPException(status_code=404, detail="Jadwal libur not found")
    
    return APIResponse(
        status_code=200,
        message="success",
        data= jadwal_libur
    )

@router.patch("/delete/{jadwal_libur_id}", response_model=APIResponse[JadwalLiburDeleted], summary="delete jadwal libur")
def delete_jadwal_libur(
    jadwal_libur_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    deleted_jadwal_libur = delete_jadwal_libur_service(db, jadwal_libur_id=jadwal_libur_id)

    if not deleted_jadwal_libur:
        raise HTTPException(status_code=404, detail="Jadwal libur not found")

    return APIResponse(
        status_code=200,
        message="Jadwal libur deleted successfully",
        data=deleted_jadwal_libur
    )