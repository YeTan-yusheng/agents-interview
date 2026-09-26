from fastapi import FastAPI,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.db import get_db
from app.api import users
app = FastAPI(title=settings.app_name,debug=settings.debug)
app.include_router(users.router)

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