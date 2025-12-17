from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.modules.auth.models import (
    RefreshToken,
    TokenType,
    User,
    UserTokenVerification,
)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_verification(self, id: int):
        await self.session.execute(
            update(User).where(User.id == id).values(is_verified=True)
        )

        await self.session.commit()


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: str, user_id: int, expires_at: datetime):
        rt = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)

        self.session.add(rt)
        await self.session.commit()

    async def get(self, token: str):
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def delete(self, token: str):
        await self.session.execute(
            delete(RefreshToken).where(RefreshToken.token == token)
        )
        await self.session.commit()


class TokenTypeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name, expires_in_minutes, single_use):
        token_type = TokenType(
            name=name,
            expires_in_minutes=expires_in_minutes,
            single_use=single_use,
        )

        self.session.add(token_type)
        await self.session.commit()

    async def get_by_name(self, name: str):
        result = await self.session.execute(
            select(TokenType).where(TokenType.name.like(name))
        )

        return result.scalar_one_or_none()

    async def get_by_id(self, id: int):
        result = await self.session.execute(
            select(TokenType).where(TokenType.id == id)
        )

        return result.scalar_one_or_none()


class UserTokenVerificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, code, token_type_id, expires_at):
        verification_token = UserTokenVerification(
            user_id=user_id,
            code=code,
            token_type_id=token_type_id,
            expires_at=expires_at,
        )

        self.session.add(verification_token)
        await self.session.commit()

    async def get_by_id(self, id: int):
        result = await self.session.execute(
            select(UserTokenVerification).where(UserTokenVerification.id == id)
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(self, id: int):
        result = await self.session.execute(
            select(UserTokenVerification).where(
                UserTokenVerification.user_id == id
            )
        )

        return result.scalar_one_or_none()

    async def set_used(self, id: int):
        await self.session.execute(
            update(UserTokenVerification)
            .where(UserTokenVerification.user_id == id)
            .values(used_at=datetime.now(timezone.utc))
        )
        await self.session.commit()
