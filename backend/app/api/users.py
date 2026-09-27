from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from fastapi.exceptions import HTTPException
from app.services import user_service
from app.schemas.user import UserCreate, UserOut, UserLogin, TokenOut
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserOut:
    return await user_service.create_user(db, payload.username, payload.password)


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenOut:
    user = await user_service.verify_login(db, payload.username, payload.password)
    return TokenOut(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user


@router.get("", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[UserOut]:
    return await user_service.list_users(db)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserOut:
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="未找到用户")
    return user
