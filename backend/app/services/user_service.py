from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.exceptions import DuplicateUsernameError
import logging

logger = logging.getLogger(__name__)


async def create_user(db: AsyncSession, username: str) -> User:
    existing = await db.scalar(select(User).where(User.username == username))

    if existing is not None:
        logger.warning("拒绝创建用户，用户名已存在 username=%s", username)
        raise DuplicateUsernameError(username)

    user = User(username=username)
    db.add(user)
    await db.commit()
    logger.info("用户创建成功 username=%s id=%s", username, user.id)
    await db.refresh(user)
    return user

async def list_users(db: AsyncSession) -> list[User]:
    users = await db.execute(select(User))
    logger.info("查询用户列表，返回 %d 条", len(users))
    return list(users.scalars().all())

async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await db.execute(select(User).where(User.id == user_id))
    return user.scalar_one_or_none()

