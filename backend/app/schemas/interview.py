from datetime import datetime

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=50, examples=["Python 后端开发"])


class QuestionOut(BaseModel):
    question: str


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
