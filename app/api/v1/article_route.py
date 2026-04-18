from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.user_route import get_db
from app.models.users import RoleEnum
from app.service.article_service import create_article_service, get_article_by_id_service, get_article_service, create_article_service
from app.schemas.article_schema import articleBaseInfo, articleCreate, articleGetResponse
from app.core.require_role import require_role

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/",response_model=articleGetResponse, summary="Get list of articles")
def get_articles(
    db: Session = Depends(get_db),
    current_page: int = 1,
    limit: int = 10,
    search: str | None = None
):
    articles = get_article_service(db, current_page, limit, search)
    return articles

@router.get("/{article_id}", response_model=articleBaseInfo, summary="Get article by ID")
def get_article_by_id(
    article_id: int,
    db: Session = Depends(get_db)
):
    article = get_article_by_id_service(db, article_id)
    return article

@router.post("/", response_model=articleBaseInfo, summary="Create a new article")
def article_create(
    payload: articleCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_role(RoleEnum.ahli_gizi))
):
    new_article = create_article_service(db, payload)
    return new_article

