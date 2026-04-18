from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

def register_exception_handlers(app):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
       return JSONResponse(
           status_code=exc.status_code,
              content={
                  "Status_code": exc.status_code,
                  "message": exc.detail,
                  "data": None
                  },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "status_code": 422,
                "message": "Validation Error",
                "data": exc.errors(),
            },
        )


