from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.users import router as users_router
from app.api.v1.workflow_runs import router as workflow_runs_router
from app.api.v1.workflows import router as workflows_router
from app.core.config import get_settings
from app.core.exceptions import (
    DocumentNotFoundError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    ResourcePermissionError,
    WorkflowNotExecutableError,
    WorkflowNotFoundError,
)

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(workflows_router, prefix="/api/v1")
app.include_router(workflow_runs_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")


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


@app.exception_handler(WorkflowNotFoundError)
async def workflow_not_found_handler(request: Request, exc: WorkflowNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ResourcePermissionError)
async def resource_permission_handler(
    request: Request, exc: ResourcePermissionError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(WorkflowNotExecutableError)
async def workflow_not_executable_handler(
    request: Request, exc: WorkflowNotExecutableError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(request: Request, exc: DocumentNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
