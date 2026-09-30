"""初始化建表"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.base import Base
import app.models
from app.core.config import settings


async def main() -> None:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


asyncio.run(main())
