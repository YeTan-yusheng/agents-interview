import logging
import os
import time
import uuid
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from contextlib import asynccontextmanager
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.agents.interview_graph import init_turn_graph
from app.core.config import settings
from app.core.db import get_db, engine
from app.core.log import setup_logging
from app.api import users, interview
from app.exceptions import (
    DuplicateUsernameError,
    InvalidCredentialsError,
    llmError,
    InterviewNotFoundError,
    InterviewCloseError,
)
from app.models.base import Base

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    os.makedirs("data",exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string("data/checkpoints.db") as saver:
        await init_turn_graph(saver)
        yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    description="agents-interview项目后端",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(users.router, prefix="/api")
app.include_router(interview.router, prefix="/api")


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


@app.exception_handler(InterviewCloseError)
async def interview_close_error_handler(request: Request, exc: InterviewCloseError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
