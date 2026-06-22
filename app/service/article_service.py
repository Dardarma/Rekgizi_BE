from math import ceil
from datetime import date
from html.parser import HTMLParser

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Article,User
from app.schemas.article_schema import articleCreate, articleUpdate
from app.utils.helpers.upload import (
    delete_article_upload,
    normalize_article_upload_url,
    resolve_article_upload_path,
)


class _ContentImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources: set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag.casefold() != "img":
            return
        source = dict(attrs).get("src")
        if source:
            self.sources.add(source)


def _article_file_paths(thumbnail_url: str | None, content: str | None) -> set[str]:
    paths: set[str] = set()
    normalized_thumbnail = normalize_article_upload_url(thumbnail_url)
    if normalized_thumbnail:
        paths.add(normalized_thumbnail)

    parser = _ContentImageParser()
    parser.feed(content or "")
    paths.update(
        normalized_source
        for source in parser.sources
        if (normalized_source := normalize_article_upload_url(source))
    )
    return paths


def _is_file_used_by_other_article(
    db: Session,
    file_url: str,
    excluded_article_id: int,
) -> bool:
    target = resolve_article_upload_path(file_url)
    if target is None:
        return False

    other_articles = (
        db.query(Article.thumbnail_url, Article.konten)
        .filter(
            Article.id != excluded_article_id,
            Article.deleted_at.is_(None),
        )
        .all()
    )
    for thumbnail_url, content in other_articles:
        for other_url in _article_file_paths(thumbnail_url, content):
            if resolve_article_upload_path(other_url) == target:
                return True
    return False


def _delete_unused_article_files(
    db: Session,
    article_id: int,
    old_files: set[str],
    new_files: set[str],
) -> None:
    for file_url in old_files - new_files:
        if not _is_file_used_by_other_article(db, file_url, article_id):
            delete_article_upload(file_url)

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

    old_files = _article_file_paths(article.thumbnail_url, article.konten)

    if payload.judul is not None:
        article.judul = payload.judul
    if payload.konten is not None:
        article.konten = payload.konten
    if payload.is_published is not None:
        article.is_published = payload.is_published
    if "thumbnail_url" in payload.model_fields_set:
        article.thumbnail_url = payload.thumbnail_url

    db.commit()
    db.refresh(article)

    new_files = _article_file_paths(article.thumbnail_url, article.konten)
    _delete_unused_article_files(db, article.id, old_files, new_files)

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

    article_files = _article_file_paths(article.thumbnail_url, article.konten)
    article.deleted_at = func.now()
    db.commit()
    db.refresh(article)

    _delete_unused_article_files(db, article.id, article_files, set())

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
