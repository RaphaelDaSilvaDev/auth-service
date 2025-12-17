from datetime import datetime, timezone

from auth_service.core.secutiry import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from auth_service.modules.auth.handlers.on_user_created import (
    SendEmailVerificationHandle,
)
from auth_service.modules.auth.models import User
from auth_service.modules.auth.repository import (
    RefreshTokenRepository,
    TokenTypeRepository,
    UserRepository,
    UserTokenVerificationRepository,
)
from auth_service.modules.auth.schemas import (
    UserCreate,
    UserCreatedEvent,
    UserLogin,
    UserLoginReturn,
    UserRefreshToken,
    ValidateAccount,
)


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
        refreshRepository: RefreshTokenRepository | None = None,
        tokenTypeRepository: TokenTypeRepository | None = None,
        userVerificationTokenRepository: UserTokenVerificationRepository
        | None = None,
    ):
        self.repository = repository
        self.refreshRepository = refreshRepository
        self.tokenTypeRepository = tokenTypeRepository
        self.userVerificationTokenRepository = userVerificationTokenRepository

    async def register(self, data: UserCreate) -> User:
        sendEmailHandle = SendEmailVerificationHandle(
            tokenTypeRepository=self.tokenTypeRepository,
            userVerificationTokenRepository=self.userVerificationTokenRepository,
        )

        existing_user = await self.repository.get_by_email(data.email)

        if existing_user:
            raise ValueError('User already exists')

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            username=data.username,
        )

        created_user = await self.repository.create(user)

        if not created_user:
            raise ValueError('User creation error')

        user_event = UserCreatedEvent(
            user_id=created_user.id,
            email=created_user.email,
            username=created_user.username,
        )

        await sendEmailHandle.handle(event=user_event)

        return created_user

    async def login(self, data: UserLogin) -> UserLoginReturn:
        if not self.refreshRepository:
            raise RuntimeError('RefreshTokenRepository not configured')

        user = await self.repository.get_by_email(data.email)

        if not user:
            raise ValueError('Invalid credentials')

        if not user.is_active:
            raise ValueError('Account not activated')

        if not user.is_verified:
            raise ValueError('Account not verified')

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

    async def validate_account(self, data: ValidateAccount):
        existing_user = await self.repository.get_by_email(data.email)

        if not existing_user:
            raise ValueError('Invalid email')

        if existing_user.is_verified:
            raise ValueError('Account already verified')

        if not existing_user.is_active:
            raise ValueError('Account is not active')

        userVerification = (
            await self.userVerificationTokenRepository.get_by_user_id(
                existing_user.id
            )
        )

        if not verify_password(data.code, userVerification.code):
            raise ValueError('Invalid code')

        if userVerification.expires_at < datetime.now(timezone.utc):
            raise ValueError('Code expired')

        await self.userVerificationTokenRepository.set_used(existing_user.id)
        await self.repository.update_verification(existing_user.id)
