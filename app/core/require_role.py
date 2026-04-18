from fastapi import HTTPException, Request

from app.models.users import RoleEnum
from app.utils.helpers.respons import APIResponse


def require_role(*allowed_roles: RoleEnum):
    def check_role(request: Request):
        user_role = getattr(request.state, "role", None)
        if user_role is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        user_role_value = user_role.value if isinstance(user_role, RoleEnum) else str(user_role)
        allowed_role_values = [role.value for role in allowed_roles]

        if user_role_value not in allowed_role_values:
            raise HTTPException(
                status_code=403,
                detail="Akses ditolak",
            )
        return request.state
    return check_role

def get_current_user(request: Request):
    user_id = getattr(request.state, "user_id", None)
    user_role = getattr(request.state, "role", None)
    if user_id is None or user_role is None:
        raise HTTPException(status_code=401, detail="horized")
    return {
        "id": user_id,
        "role": user_role
    }