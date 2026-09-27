from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.exceptions import DuplicateUsernameError,InvalidCredentialsError
import logging
from app.core.security import hash_password, verify_password


logger = logging.getLogger(__name__)


async def create_user(db: AsyncSession, username: str,password: str) -> User:
    existing = await db.scalar(select(User).where(User.username == username))

    if existing is not None:
        logger.warning("拒绝创建用户，用户名已存在 username=%s", username)
        raise DuplicateUsernameError(username)

    user = User(username=username,password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("用户创建成功 username=%s id=%s", username, user.id)
    return user

async def verify_login(db: AsyncSession,username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(password, user.password_hash):
        logger.warning("登录失败 username=%s", username)
        raise InvalidCredentialsError()

    logger.info("登录成功 username=%s id=%s", username, user.id)
    return user


async def list_users(db: AsyncSession) -> list[User]:
    users = await db.execute(select(User))
    users_list = users.scalars().all()

    logger.info("查询用户列表，返回 %d 条", len(users_list))
    return users_list

async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await db.execute(select(User).where(User.id == user_id))
    return user.scalar_one_or_none()

