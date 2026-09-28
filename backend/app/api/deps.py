from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services import user_service

# FastAPI 的声明，本应用的 token 从 /users/token 接口获取
# OAuth2PasswordBearer 自动从请求头解析 Bearer xxx
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/users/token", auto_error=False)


async def get_current_user(
        token: str = Depends(oauth_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    if token is None:
        raise HTTPException(status_code=401, detail="未登录")

    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = await user_service.get_user(db, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user
