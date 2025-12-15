from auth_service.core.secutiry import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from auth_service.modules.auth.models import User
from auth_service.modules.auth.repository import UserRepository
from auth_service.modules.auth.schemas import (
    UserCreate,
    UserLogin,
    UserLoginReturn,
)


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

    async def login(self, data: UserLogin) -> UserLoginReturn:
        user = await self.repository.get_by_email(data.email)

        if not user:
            raise ValueError('Invalid credentials')

        if not verify_password(data.password, user.password_hash):
            raise ValueError('Invalid credentials')

        return UserLoginReturn(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
