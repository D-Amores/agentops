from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.core.config import get_settings
from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.exception_handler(EmailAlreadyExistsError)
async def email_already_exists_handler(
    request: Request, exc: EmailAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})
