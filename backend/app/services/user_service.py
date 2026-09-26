from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

async def create_user(db: AsyncSession, username: str) -> User:
    user = User(username=username)
    db.add(user)
    await db.commit()
    return user

async def list_users(db: AsyncSession) -> list[User]:
    users = await db.execute(select(User))
    return list(users.scalars().all())

async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await db.execute(select(User).where(User.id == user_id))
    return user.scalar_one_or_none()

