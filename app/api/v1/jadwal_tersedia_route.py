from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.auth_route import get_db
from app.utils.helpers.respons import APIResponse
from app.service.jadwal_konseling.jadwal_tersedia_service import delete_jadwal_tersedia_service, edit_jadwal_tersedia_service, get_jadwal_tersedia_by_id_service, get_jadwal_tersedia_service, post_jadwal_tersedia_service, get_jadwal_tersedia_by_user_service
from app.schemas.jadwal_tersedia_schema import JadwalTersediaCreate, JadwalTersediaListInfo, JadwalTersediaUpdate, jadwalTersediaBasicInfo
from app.core.require_role import require_role
from app.models.users import RoleEnum

router = APIRouter(prefix="/jadwal-tersedia", tags=["jadwal-tersedia"])

@router.get("/",response_model=APIResponse[JadwalTersediaListInfo], summary="Get Jadwal 7 hari kedepan")
def get_jadwal_tersedia(
    db: Session = Depends(get_db)
):
    jadwal_tersedia = get_jadwal_tersedia_service(db)

    return APIResponse(
        status_code=200,
        message="success",
        data={"jadwal_tersedia": jadwal_tersedia}
)

@router.get("/user", response_model=APIResponse[list[jadwalTersediaBasicInfo]], summary="Get jadwal tersedia berdasarkan user yang sedang login")
def get_jadwal_tersedia_by_user(
    state = Depends(require_role(RoleEnum.ahli_gizi)),
    db: Session = Depends(get_db)
):
    user_id = state.user_id
    jadwal = get_jadwal_tersedia_by_user_service(db, user_id)

    return APIResponse(
        status_code=200,
        message="success",
        data= jadwal
    )

@router.post("/",response_model=APIResponse[jadwalTersediaBasicInfo],summary="upload jadwal tersedia")
def create_jadwal_tersedia(
    payload: JadwalTersediaCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    jadwal_tersedia = post_jadwal_tersedia_service(db, payload)

    return APIResponse(
        status_code=201,
        message="Jadwal tersedia created successfully",
        data= jadwal_tersedia
    ) 

@router.get("/{id}", response_model=APIResponse[jadwalTersediaBasicInfo], summary="Get jadwal tersedia by ID")
def get_jadwal_tersedia_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    jadwal_tersedia = get_jadwal_tersedia_by_id_service(db,id)

    return APIResponse(
        status_code=200,
        message="success",
        data= jadwal_tersedia
    )

@router.patch("/{id}", response_model=APIResponse[jadwalTersediaBasicInfo], summary="Edit jadwal tersedia by ID")
def edit_jadwal_tersedia(
    id: int,
    payload: JadwalTersediaUpdate ,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    jadwal_tersedia = edit_jadwal_tersedia_service(db, id, payload)

    return APIResponse(
        status_code=200,
        message="Jadwal tersedia updated successfully",
        data= jadwal_tersedia
    )

@router.patch("/delete/{id}")
def delete_jadwal_tersedia(
    id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    result = delete_jadwal_tersedia_service(db, id)

    return APIResponse(
        status_code=200,
        message="Jadwal tersedia deleted successfully",
        data=None
    )