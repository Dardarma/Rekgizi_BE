import os
import uuid
import shutil
import logging
from pathlib import Path
from urllib.parse import unquote, urlparse
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def get_file_extension(filename: str) -> str:
    return filename.split(".")[-1].lower() if "." in filename else ""

def is_allowed_extension(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

def validate_file(file: UploadFile):
    if not is_allowed_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File tidak diizinkan. Ekstensi yang diperbolehkan: {', '.join(ALLOWED_EXTENSIONS)}"
        )
        
    # Validasi ukuran file
    file.file.seek(0, 2)  # Pindah ke akhir file
    size = file.file.tell()  # Dapatkan ukuran file (posisi saat ini)
    file.file.seek(0)  # Kembalikan ke awal file
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail="Ukuran file terlalu besar. Maksimal 5MB."
        )

def save_upload_file(upload_file: UploadFile, destination_folder: str) -> str:
    """
    Menyimpan file upload ke direktori tujuan dan mengembalikan relative path.
    """
    validate_file(upload_file)

    # Generate unique filename dengan UUID
    ext = get_file_extension(upload_file.filename)
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Pastikan direktori tujuan ada
    os.makedirs(destination_folder, exist_ok=True)
    
    # Path file lengkap
    file_path = os.path.join(destination_folder, unique_filename)
    
    # Simpan file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    # Gunakan forward slash untuk URL consistency di berbagai OS
    relative_path = file_path.replace("\\", "/")
    
    return relative_path


ARTICLE_UPLOAD_ROOT = Path("static/uploads/articles").resolve()
logger = logging.getLogger(__name__)


def resolve_article_upload_path(file_url: str | None) -> Path | None:
    """Resolve URL/path upload artikel dan tolak path di luar folder artikel."""
    if not file_url:
        return None

    parsed_path = unquote(urlparse(str(file_url)).path).lstrip("/").replace("\\", "/")
    candidate = Path(parsed_path).resolve()
    try:
        candidate.relative_to(ARTICLE_UPLOAD_ROOT)
    except ValueError:
        return None
    return candidate


def delete_article_upload(file_url: str | None) -> bool:
    """Hapus file upload artikel secara aman; URL eksternal selalu diabaikan."""
    file_path = resolve_article_upload_path(file_url)
    if file_path is None or not file_path.is_file():
        return False
    try:
        file_path.unlink()
        return True
    except OSError:
        logger.exception("Gagal menghapus file upload artikel: %s", file_path)
        return False


def normalize_article_upload_url(file_url: str | None) -> str | None:
    file_path = resolve_article_upload_path(file_url)
    if file_path is None:
        return None
    relative_path = file_path.relative_to(ARTICLE_UPLOAD_ROOT)
    return f"/static/uploads/articles/{relative_path.as_posix()}"
