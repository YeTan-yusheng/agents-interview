from datetime import datetime
from app.models.base import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String, DateTime, func


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    username: Mapped[str] = mapped_column(String(20),unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now())
    password_hash: Mapped[str] = mapped_column(String(255))
