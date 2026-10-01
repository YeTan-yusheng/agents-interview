from datetime import datetime

from pydantic import BaseModel, Field


class InterviewCreate(BaseModel):
    topic: str = Field(min_length=2, max_length=50, examples=["Python 后端开发"])


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InterviewOut(BaseModel):
    id: int
    topic: str
    status: str
    created_at: datetime
    messages: list[MessageOut] = []

    model_config = {"from_attributes": True}


class AnswerCreate(BaseModel):
    content: str = Field(min_length=1,max_length=2000,examples=["索引是把查询从全表扫描优化为树查找"])