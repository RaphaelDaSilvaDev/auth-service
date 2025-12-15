from auth_service.core.secutiry import hash_password
from auth_service.modules.auth.models import User
from auth_service.modules.auth.repository import UserRepository
from auth_service.modules.auth.schemas import UserCreate


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, data: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(data.email)

        if existing_user:
            raise ValueError('User already exists')

        user = User(
            email=data.email, password_hash=hash_password(data.password)
        )

        return await self.repository.create(user)
