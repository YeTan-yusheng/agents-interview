import logging
import time
import uuid
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.core.db import get_db
from app.core.log import setup_logging
from app.api import users, interview
from app.exceptions import (
    DuplicateUsernameError,
    InvalidCredentialsError,
    llmError,
    InterviewNotFoundError
)

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    description="agents-interview项目后端",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(interview.router)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = uuid.uuid4().hex[:8]
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.0fms) [%s]",
        request.method, request.url.path, response.status_code, duration_ms, request_id,
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", tags=["运维"],
         summary="健康检查")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/about", tags=["运维"],
         summary="应用信息")
async def about() -> dict[str, str]:
    return {"app": settings.app_name, "debug": str(settings.debug)}


@app.get("/db-check", tags=["运维"],
         summary="数据库连接检查")
async def db_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.exception_handler(DuplicateUsernameError)
async def duplicate_username_handler(request: Request, exc: DuplicateUsernameError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(llmError)
async def llm_error_handler(request: Request, exc: llmError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(InterviewNotFoundError)
async def interview_not_found_handler(request: Request, exc: InterviewNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
