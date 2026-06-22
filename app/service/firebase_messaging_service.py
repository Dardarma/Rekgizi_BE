import json
import logging
import os
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_messaging_client():
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging
    except ImportError:
        logger.warning("firebase-admin belum terinstall di environment backend")
        return None, None

    if not firebase_admin._apps:
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

        if service_account_path:
            cred = credentials.Certificate(service_account_path)
        elif service_account_json:
            cred = credentials.Certificate(json.loads(service_account_json))
        else:
            logger.warning("Firebase service account belum dikonfigurasi")
            return None, None

        firebase_admin.initialize_app(cred)

    return firebase_admin, messaging


def send_push_notification(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
):
    valid_tokens = [token for token in tokens if token]
    if not valid_tokens:
        logger.warning("Tidak ada FCM token tujuan untuk push notification")
        return None

    _, messaging = _get_messaging_client()
    if messaging is None:
        logger.warning("Firebase messaging client tidak tersedia")
        return None

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data={key: str(value) for key, value in (data or {}).items()},
        tokens=valid_tokens,
    )

    response = messaging.send_each_for_multicast(message)
    logger.info(
        "Push notification terkirim: success=%s failure=%s",
        response.success_count,
        response.failure_count,
    )
    return response
