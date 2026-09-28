import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate


def test_valid_input_passes():
    u = UserCreate(username="zhangsan", password="password123")
    assert u.username == "zhangsan"


@pytest.mark.parametrize(
    "bad_username",
    [
        "s",  # 太短
        "x" * 60,  # 太长
        "has space",  # 包含空格
        "符号！"  # 包含特殊字符
    ],
)
def test_invalid_username_rejected(bad_username):
    with pytest.raises(ValidationError):
        UserCreate(username=bad_username, password="password123")


@pytest.mark.parametrize(
    "bad_password",
    [
        "a",  # 太短
        "x" * 73,  # 太长
        "",  # 空串
    ],
)
def test_invalid_password_rejected(bad_password):
    with pytest.raises(ValidationError):
        UserCreate(username="zhangsan", password=bad_password)
