from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)

AsyncSessionLocal = async_sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with AsyncSessionLocal() as db:
        yield db
