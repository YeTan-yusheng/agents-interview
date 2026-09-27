from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from fastapi.exceptions import HTTPException
from app.services import user_service
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users",tags=["users"])

@router.post("",response_model=UserOut,status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserOut:
    return  await user_service.create_user(db, payload.username)

@router.get("",response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[UserOut]:
    return await user_service.list_users(db)

@router.get("/{user_id}",response_model=UserOut)
async def get_user(user_id: int,db: AsyncSession = Depends(get_db)) -> UserOut:
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404,detail="未找到用户")
    return user
