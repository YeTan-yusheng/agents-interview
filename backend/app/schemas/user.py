from pydantic import BaseModel, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(min_length=2,max_length=20,pattern=r"^\w+$",examples=["zhangsan"])
    password: str = Field(min_length=6,max_length=72,examples=["password123"])

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token: str = Field(examples=["token123456"])
    token_type: str = "bearer"
