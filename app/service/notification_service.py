from sqlalchemy.orm import Session

from app.models.notification_token import NotificationToken
from app.schemas.notification_schema import NotificationTokenCreate
from app.service.firebase_messaging_service import send_push_notification


def save_notification_token_service(
    db: Session,
    user_id: int,
    payload: NotificationTokenCreate,
):
    notification_token = (
        db.query(NotificationToken)
        .filter(NotificationToken.token == payload.token)
        .first()
    )

    if notification_token:
        notification_token.user_id = user_id
        notification_token.device_type = payload.device_type
    else:
        notification_token = NotificationToken(
            user_id=user_id,
            token=payload.token,
            device_type=payload.device_type,
        )
        db.add(notification_token)

    db.commit()
    db.refresh(notification_token)
    return notification_token


def get_user_notification_tokens(db: Session, user_id: int):
    return (
        db.query(NotificationToken.token)
        .filter(NotificationToken.user_id == user_id)
        .all()
    )


def send_jadwal_konseling_notification(db: Session, jadwal):
    tokens = [item.token for item in get_user_notification_tokens(db, jadwal.konselor_id)]

    try:
        return send_push_notification(
            tokens=tokens,
            title="Janji temu baru",
            body=f"{jadwal.nama_pasien} mengajukan janji temu pada {jadwal.tanggal_konseling}.",
            data={
                "type": "jadwal_konseling_created",
                "jadwal_id": jadwal.id,
                "pasien_id": jadwal.pasien_id,
                "konselor_id": jadwal.konselor_id,
                "tanggal_konseling": jadwal.tanggal_konseling,
            },
        )
    except Exception:
        return None
