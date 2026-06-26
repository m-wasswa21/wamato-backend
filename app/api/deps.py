import uuid
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import Unauthorized, Forbidden
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise Unauthorized("Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise Unauthorized()
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise Unauthorized("User not found or inactive")
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise Unauthorized("Inactive user")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise Forbidden("Admin access required")
    return user


async def require_agent_or_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in (UserRole.agent, UserRole.admin):
        raise Forbidden("Agent or admin access required")
    return user
