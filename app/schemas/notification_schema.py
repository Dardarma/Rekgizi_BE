from pydantic import BaseModel


class NotificationTokenCreate(BaseModel):
    token: str
    device_type: str | None = "web"


class NotificationTokenInfo(BaseModel):
    id: int
    user_id: int
    token: str
    device_type: str | None = None

    model_config = {
        "from_attributes": True
    }
