from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services import interview_service
from app.schemas.interview import InterviewOut, InterviewCreate,AnswerCreate

router = APIRouter(prefix="/interview", tags=["面试"])


@router.post("", response_model=InterviewOut, status_code=201,
             summary="开一场新面试：创建会话并生成第一题。（需要登录）")
async def start(
        payload: InterviewCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
) -> InterviewOut:
    """开一场新面试：创建会话并生成第一题。"""
    return await interview_service.start_interview(db, current_user.id, payload.topic)


@router.get("/{interview_id}", response_model=InterviewOut,
            summary="根据面试ID获取面试详情（需要登录）。")
async def read_interview(
        interview_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> InterviewOut:
    """获取面试详情（需要登录）。"""
    return await interview_service.get_interview(db, interview_id, current_user.id)


@router.get("", response_model=list[InterviewOut],
            summary="获取用户所有面试会话（需要登录）。")
async def list_interviews(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> list[InterviewOut]:
    """获取用户所有面试会话（需要登录）。"""
    return await interview_service.list_interviews(db, current_user.id)


@router.post("/{interview_id}/answer",response_model=InterviewOut,
             summary="提交回答并获得面试官的追问（需要登录）。")
async def answer_interview(
        interview_id: int,
        payload: AnswerCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
) -> InterviewOut:
    """提交回答并获得面试官的追问（需要登录）。"""
    return await interview_service.answer_interview(db, interview_id, current_user.id, payload.content)


@router.post("/{interview_id}/finish")
async def finish_interview(
        interview_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
) -> InterviewOut:
    """结束面试（需要登录）。"""
    return await interview_service.finish_interview(db, interview_id, current_user.id)

