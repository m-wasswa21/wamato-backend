from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, ChangePasswordRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import Conflict, Unauthorized, BadRequest


class AuthService:

    @staticmethod
    async def register(db: AsyncSession, body: RegisterRequest) -> User:
        existing = await db.execute(select(User).where(User.email == body.email))
        if existing.scalar_one_or_none():
            raise Conflict("Email already registered")
        user = User(
            full_name=body.full_name,
            email=body.email,
            phone=body.phone,
            hashed_password=hash_password(body.password),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, body: LoginRequest) -> TokenResponse:
        result = await db.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(body.password, user.hashed_password):
            raise Unauthorized("Invalid email or password")
        if not user.is_active:
            raise Unauthorized("Account is deactivated")
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    @staticmethod
    async def refresh(db: AsyncSession, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise Unauthorized("Invalid refresh token")
        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise Unauthorized()
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    @staticmethod
    async def change_password(db: AsyncSession, user: User, body: ChangePasswordRequest) -> None:
        if not verify_password(body.current_password, user.hashed_password):
            raise BadRequest("Current password is incorrect")
        user.hashed_password = hash_password(body.new_password)
        db.add(user)
