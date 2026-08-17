import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
try:
    from app.database import get_db
except ModuleNotFoundError:
    try:
        from database import get_db
    except ModuleNotFoundError:
        from database import get_db
try:
    from app.models import User
except ModuleNotFoundError:
    try:
        from models import User
    except ModuleNotFoundError:
        from models import User
try:
    from app.config import settings
except ModuleNotFoundError:
    try:
        from config import settings
    except ModuleNotFoundError:
        from config import settings

SECRET_KEY = getattr(settings, "SECRET_KEY", "pusulamnet-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer(auto_error=False)

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if not hashed_password:
            return False
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    HTTP Authorization Bearer token başlığından oturum açmış kullanıcıyı bulur.
    Eğer geçerli token yoksa HTTP 401 Unauthorized fırlatır.
    """
    if not credentials or not credentials.credentials:
        # Fallback: Eğer hiç kullanıcı yoksa ilk varsayılan kullanıcıyı al, varsa yetkisiz hatası ver
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oturum süreniz doldu veya giriş yapmadınız.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = AuthService.decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş kimlik doğrulama jetonu.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
