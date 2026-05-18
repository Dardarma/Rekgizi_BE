from math import ceil

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Article,User
from app.schemas.article_schema import articleCreate

def get_article_service(
    db: Session,
    current_page: int = 1,
    limit: int = 10,
    search: str | None = None
):
    query = (
        db.query(
            Article,
            User.nama.label("nama_pembuat")
        )
        .join(User, Article.user_id == User.id)
        .filter(Article.deleted_at.is_(None))
    )

    if search:
        query = query.filter(Article.judul.ilike(f"%{search}%"))

    total = query.count()

    if total == 0:
        return {
            "data": [],
            "meta": {
                "current_page": current_page,
                "limit": limit,
                "total": 0,
                "total_pages": 0
            }
        }

    offset = (current_page - 1) * limit

    articles = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_page = ceil(total / limit) if limit > 0 else 1
    result = []
    for art, nama_pembuat in articles:
        result.append({
            "id": art.id,
            "user_id": art.user_id,
            "nama_pembuat": nama_pembuat,
            "judul": art.judul,
            "konten": art.konten,
            "url_thumbnail": art.thumbnail_url,
            "is_published": art.is_published,
            "tanggal": art.created_at.date()
        })

    return {
        "data": result,
        "meta": {
            "current_page": current_page,
            "limit": limit,
            "total": total,
            "total_pages": total_page
        }
    }

def get_article_by_id_service(
    db: Session,
    article_id : int
):
    article = (
        db.query(
            Article,
            User.nama.label("nama_pembuat")
        )
        .join(User, Article.user_id == User.id)
        .filter(Article.id == article_id, Article.deleted_at.is_(None))
        .first()
    )

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    art, nama_pembuat = article

    return {
        "id": art.id,
        "user_id": art.user_id,
        "nama_pembuat": nama_pembuat,
        "judul": art.judul,
        "konten": art.konten,
        "is_published": art.is_published,
        "url_thumbnail": art.thumbnail_url,
        "tanggal": art.created_at.date()
    }

def create_article_service(
    db: Session,
    payload: articleCreate
):

    new_article = Article(
        user_id= payload.user_id,
        judul= payload.judul,
        konten= payload.konten,
        is_published= payload.is_published,
    )

    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    new_article.nama_pembuat = db.query(User.nama).filter(User.id == new_article.user_id).first()[0]

    return new_article

def update_article_service(
    db: Session,
    article_id: int,
    payload: articleCreate
):
    article = db.query(Article).filter(Article.id == article_id, Article.deleted_at.is_(None)).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.judul = payload.judul
    article.konten = payload.konten
    article.is_published = payload.is_published
    article.thumbnail_url = payload.url_thumbnail

    db.commit()
    db.refresh(article)

    article.nama_pembuat = db.query(User.nama).filter(User.id == article.user_id).first()[0]

    return article

def delete_article_service(
        db: Session,
        article_id:int
):
    article = db.query(Article).filter(Article.id == article_id, Article.deleted_at.is_(None)).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article.deleted_at = func.now()
    db.commit()
    db.refresh(article)

    article.nama_pembuat = db.query(User.nama).filter(User.id == article.user_id).first()[0]

    return {
        "message": "Article deleted successfully",
        "data": {
            "id": article.id,
            "user_id": article.user_id,
            "judul": article.judul,
            "konten": article.konten,
            "is_published": article.is_published,
            "nama_pembuat": article.nama_pembuat
        }
    }
    