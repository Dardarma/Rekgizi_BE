from math import ceil
from datetime import date

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Article,User
from app.schemas.article_schema import articleCreate, articleUpdate

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
        .filter(Article.is_published == True)
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
            "thumbnail_url": art.thumbnail_url,
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

def get_article_admin_service(
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
            "thumbnail_url": art.thumbnail_url,
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
        "thumbnail_url": art.thumbnail_url,
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
        thumbnail_url= payload.thumbnail_url,
    )

    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    user = db.query(User.nama).filter(User.id == new_article.user_id).first()
    nama_pembuat = user[0] if user else ""

    return {
        "id": new_article.id,
        "user_id": new_article.user_id,
        "nama_pembuat": nama_pembuat,
        "judul": new_article.judul,
        "konten": new_article.konten,
        "is_published": new_article.is_published,
        "thumbnail_url": new_article.thumbnail_url,
        "tanggal": new_article.created_at.date() if new_article.created_at else date.today()
    }

def update_article_service(
    db: Session,
    article_id: int,
    payload: articleUpdate
):
    article = db.query(Article).filter(Article.id == article_id, Article.deleted_at.is_(None)).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if payload.judul is not None:
        article.judul = payload.judul
    if payload.konten is not None:
        article.konten = payload.konten
    if payload.is_published is not None:
        article.is_published = payload.is_published
    if payload.thumbnail_url is not None:
        article.thumbnail_url = payload.thumbnail_url

    db.commit()
    db.refresh(article)

    user = db.query(User.nama).filter(User.id == article.user_id).first()
    nama_pembuat = user[0] if user else ""

    return {
        "id": article.id,
        "user_id": article.user_id,
        "nama_pembuat": nama_pembuat,
        "judul": article.judul,
        "konten": article.konten,
        "is_published": article.is_published,
        "thumbnail_url": article.thumbnail_url,
        "tanggal": article.created_at.date() if article.created_at else date.today()
    }

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
    