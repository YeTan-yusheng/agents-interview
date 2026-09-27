import logging
import time
import uuid
from fastapi import FastAPI,Depends,Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.db import get_db
from app.core.log import setup_logging
from app.api import users
from app.exceptions import DuplicateUsernameError, InvalidCredentialsError


setup_logging(settings.log_level)
logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name,debug=settings.debug)
app.include_router(users.router)


@app.middleware("http")
async def request_logging(request: Request,call_next):
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

@app.get("/health")
async def health_check() -> dict[str,str]:
    return {"status": "ok"}


@app.get("/about")
async def about() -> dict[str,str]:
    return {"app": settings.app_name,"debug": str(settings.debug)}

@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)) -> dict[str,str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.exception_handler(DuplicateUsernameError)
async def duplicate_username_handler(
        request: Request,exc: DuplicateUsernameError
)->JSONResponse:
    return JSONResponse(status_code=409,content={"detail": str(exc)})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})