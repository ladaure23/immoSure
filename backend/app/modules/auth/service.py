from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from jose import jwt
import bcrypt
from app.config import settings
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _create_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user.id), "role": user.role, "agence_id": str(user.agence_id) if user.agence_id else None, "exp": expire},
        settings.secret_key,
        algorithm="HS256",
    )


async def login(email: str, password: str, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not _verify(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    return TokenResponse(access_token=_create_token(user), role=user.role, agence_id=user.agence_id)


async def register(payload: RegisterRequest, db: AsyncSession) -> TokenResponse:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email déjà utilisé")
    user = User(
        email=payload.email,
        password_hash=_hash(payload.password),
        role="agence",
        agence_id=payload.agence_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=_create_token(user), role=user.role, agence_id=user.agence_id)
