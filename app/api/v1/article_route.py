from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.api.v1.user_route import get_db
from app.models.users import RoleEnum
from app.service.article_service import (
    create_article_service,
    get_article_admin_service,
    get_article_by_id_service, 
    get_article_service,
    update_article_service,
    delete_article_service
)
from app.schemas.article_schema import (
    articleBaseInfo, 
    articleCreate, 
    articleGetResponse, 
    articleUpdate,
    articleAPIResponse
)
from app.core.require_role import require_role
from app.utils.helpers.upload import save_upload_file
from app.utils.helpers.respons import APIResponse

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/",response_model=articleGetResponse, summary="Get list of articles")
def get_articles(
    db: Session = Depends(get_db),
    current_page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    articles = get_article_service(db, current_page, limit, search)
    return articles

@router.get("/admin",response_model=articleGetResponse, summary="Get list of articles admin")
def get_articles(
    current_page: int = 1,
    limit: int = 10,
    search: str | None = None,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    articles = get_article_admin_service(db, current_page, limit, search)
    return articles

@router.get("/{article_id}", response_model=articleAPIResponse, summary="Get article by ID")
def get_article_by_id(
    article_id: int,
    db: Session = Depends(get_db)
):
    article = get_article_by_id_service(db, article_id)
    return APIResponse(
        status_code=200,
        message="success",
        data=article
    )

@router.post("/", response_model=articleBaseInfo, summary="Create a new article")
def article_create(
    payload: articleCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    new_article = create_article_service(db, payload)
    return new_article

@router.put("/{article_id}", response_model=articleBaseInfo, summary="Update an existing article")
def article_update(
    article_id: int,
    payload: articleUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    updated_article = update_article_service(db, article_id, payload)
    return updated_article

@router.delete("/{article_id}", summary="Delete an article")
def article_delete(
    article_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    return delete_article_service(db, article_id)

@router.post("/upload/image", summary="Upload image for Quill Editor")
def upload_quill_image(
    file: UploadFile = File(...),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    file_path = save_upload_file(file, "static/uploads/articles/images")
    return {"url": f"/{file_path}"}

@router.post("/upload/thumbnail", summary="Upload thumbnail for Article")
def upload_thumbnail(
    file: UploadFile = File(...),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    file_path = save_upload_file(file, "static/uploads/articles/thumbnails")
    return {"url": f"/{file_path}"}
