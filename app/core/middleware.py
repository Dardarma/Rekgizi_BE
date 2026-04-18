from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM
import logging

logger = logging.getLogger(__name__)


def _auth_error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "Status_code": status_code,
            "message": message,
            "data": None,
        },
    )

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        methode = request.method

        PUBLIC_PATHS = {
            "/api/v1/login",
            "/api/v1/register",
        }

        PUBLIC_PREFIX_METHOD_PATHS = {
            ("GET", "/api/v1/articles"),
        }

        PUBLIC_PREFIXES = ("/docs", "/redoc", "/openapi.json")
        
        if request.method == "OPTIONS":
            return await call_next(request)

        if (
            path in PUBLIC_PATHS
            or any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES)
            or any(
                methode == m and path.startswith(prefix)
                for m, prefix in PUBLIC_PREFIX_METHOD_PATHS
            )
        ):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return _auth_error(401, "Unauthorized")

        try:
            parts = auth_header.split()
            if len(parts) != 2:
                return _auth_error(401, "Invalid Authorization header format")

            scheme, token = parts
            if scheme.lower() != "bearer":
                return _auth_error(401, "Invalid authentication scheme")

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = int(payload.get("sub"))
            request.state.role = payload.get("role")
        except JWTError as exc:
            logger.warning("JWT decode failed: %s", exc)
            return _auth_error(401, "Invalid token")

        response = await call_next(request)
        return response

