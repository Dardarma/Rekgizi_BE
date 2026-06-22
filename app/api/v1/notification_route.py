from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth_route import get_db
from app.core.require_role import require_role
from app.models.users import RoleEnum
from app.schemas.notification_schema import NotificationTokenCreate, NotificationTokenInfo
from app.service.notification_service import save_notification_token_service
from app.utils.helpers.respons import APIResponse


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/token", response_model=APIResponse[NotificationTokenInfo], summary="Save FCM token")
def save_notification_token(
    payload: NotificationTokenCreate,
    db: Session = Depends(get_db),
    state=Depends(require_role(RoleEnum.ahli_gizi)),
):
    notification_token = save_notification_token_service(
        db=db,
        user_id=state.user_id,
        payload=payload,
    )

    return APIResponse(
        status_code=200,
        message="Notification token saved successfully",
        data=notification_token,
    )
