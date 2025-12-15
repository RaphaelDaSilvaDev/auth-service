from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.modules.auth.models import RefreshToken, User


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
