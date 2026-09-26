from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from fastapi.exceptions import HTTPException
from app.services import user_service

router = APIRouter(prefix="/users",tags=["users"])

@router.post("")
async def create_user(username: str, db: AsyncSession = Depends(get_db)) -> dict:
    user = await user_service.create_user(db, username)
    return {"id": user.id, "username": user.username,"created_at": user.created_at}

@router.get("")
async def list_users(db: AsyncSession = Depends(get_db)) -> list[dict]:
    users = await user_service.list_users(db)
    return [{"id": u.id, "username": u.username,"created_at": u.created_at} for u in users]

@router.get("/{user_id}")
async def get_user(user_id: int,db: AsyncSession = Depends(get_db)) -> dict:
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404,detail="未找到用户")
    return {"id": user.id, "username": user.username,"created_at": user.created_at}
