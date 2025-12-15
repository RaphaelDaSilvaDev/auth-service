from datetime import datetime, timezone

from auth_service.core.secutiry import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from auth_service.modules.auth.models import User
from auth_service.modules.auth.repository import (
    RefreshTokenRepository,
    UserRepository,
)
from auth_service.modules.auth.schemas import (
    UserCreate,
    UserLogin,
    UserLoginReturn,
    UserRefreshToken,
)


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
        refreshRepository: RefreshTokenRepository | None = None,
    ):
        self.repository = repository
        self.refreshRepository = refreshRepository

    async def register(self, data: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(data.email)

        if existing_user:
            raise ValueError('User already exists')

        user = User(
            email=data.email, password_hash=hash_password(data.password)
        )

        return await self.repository.create(user)

    async def login(self, data: UserLogin) -> UserLoginReturn:
        if not self.refreshRepository:
            raise RuntimeError('RefreshTokenRepository not configured')

        user = await self.repository.get_by_email(data.email)

        if not user:
            raise ValueError('Invalid credentials')

        if not verify_password(data.password, user.password_hash):
            raise ValueError('Invalid credentials')

        access_token = create_access_token(user.id)
        refresh_token, refresh_expire = create_refresh_token(user.id)

        await self.refreshRepository.create(
            refresh_token, user.id, refresh_expire
        )

        return UserLoginReturn(
            access_token=access_token, refresh_token=refresh_token
        )

    async def refresh(self, refresh_token: str) -> UserRefreshToken:
        if not self.refreshRepository:
            raise RuntimeError('RefreshTokenRepository not configured')

        payload = decode_token(refresh_token)
        if payload.get('type') != 'refresh':
            raise ValueError('Invalid token')

        stored = await self.refreshRepository.get(refresh_token)
        if not stored:
            raise ValueError('Invalid token')

        if stored.expires_at < datetime.now(timezone.utc):
            await self.refreshRepository.delete(refresh_token)
            raise ValueError('Token expired')

        return UserRefreshToken(
            access_token=create_access_token(stored.user_id)
        )

    async def logout(self, refresh_token: str):
        if not self.refreshRepository:
            raise RuntimeError('RefreshTokenRepository not configured')
        await self.refreshRepository.delete(refresh_token)
