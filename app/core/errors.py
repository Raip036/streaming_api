#this file decides every failure status code

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

#----Base Class----
class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str, details: list[dict[str, str]] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or []

class InvalidRequest(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"

class UnderAge(AppError):
    status_code = 403
    code = "UNDER_AGE"

class CardNotRegistered(AppError):
    status_code = 404
    code = "CARD_NOT_REGISTERED"

class UsernameTaken(AppError):
    status_code = 409
    code= "USERNAME_TAKEN"

#---creates a JSON response used by all errors
def error_response(status_code: int, code: str, message: str, details: list[dict[str, str]] | None = None
) -> JSONResponse:
    body = {"error": {"code": code, "message": message, "details": details or []}}
    return JSONResponse(status_code=status_code, content=body)

def _field_name(location: tuple) -> str:
     #"""Turn ('body', 'password') into 'password'."""
    parts = [str(part) for part in location if part not in ("body", "query")]
    return ".".join(parts) or "body"


def register_error_handlers(app: FastAPI) -> None:
    #when an AppError happens or subclass, call this function
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = []
        for error in exc.errors():
            if error["type"] == "json_invalid":
                details.append({"field": "body", "problem": "Body is not valid JSON" })
                continue
            details.append(
                {
                    "field": _field_name(error["loc"]),
                    "problem": error["msg"].removeprefix("Value error, "),
                }
            )
        return error_response(400, "VALIDATION_ERROR", "Request failed validation", details)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return error_response(500, "INTERNAL_ERROR", "Something went wrong")

