import bcrypt
from datetime import datetime, timezone,timedelta
import jwt
from app.core.config import settings

def hash_password(plain: str):
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token,settings.jwt_secret,algorithms=["HS256"])
        return int(payload["sub"])
    except jwt.PyJWTError:
        return None