from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from fastapi.exceptions import HTTPException
from app.services import user_service
from app.schemas.user import UserCreate, UserOut, UserLogin, TokenOut
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.models.user import User
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=201,
             summary="注册用户",
             responses={409: {"description": "用户名已存在"}})
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserOut:
    """用户名全局唯一，密码经 bcrypt 哈希后存储，响应中不包含密码字段"""
    return await user_service.create_user(db, payload.username, payload.password)


@router.post("/login", response_model=TokenOut,
             summary="登录用户",
             responses={401: {"description": "用户名或密码错误"}})
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenOut:
    """登录用户，返回访问令牌"""
    user = await user_service.verify_login(db, payload.username, payload.password)
    return TokenOut(access_token=create_access_token(user.id))


@router.post("/token", response_model=TokenOut,
             summary="获取访问令牌，表单格式，供/docs的Authorize使用",
             responses={401: {"description": "用户名或密码错误"}})
async def login_for_token(
        form: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
) -> TokenOut:
    """与/login接口相同，但按 OAuth2 规范接收表单字段，专供 Swagger Authorize 调用。"""
    user = await user_service.verify_login(db, form.username, form.password)
    return TokenOut(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut,
            summary="获取当前登录信息",
            responses={404: {"description": "用户不存在"}})
async def read_me(current_user: User = Depends(get_current_user)) -> UserOut:
    """获取当前登录用户的信息"""
    return current_user


@router.get("", response_model=list[UserOut],
            summary="获取所有用户",
            responses={404: {"description": "未找到用户"}})
async def list_users(db: AsyncSession = Depends(get_db)) -> list[UserOut]:
    """获取所有用户的信息"""
    return await user_service.list_users(db)


@router.get("/{user_id}", response_model=UserOut,
            summary="获取用户信息",
            responses={404: {"description": "用户不存在"}})
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserOut:
    """获取指定用户的信息"""
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="未找到用户")
    return user
