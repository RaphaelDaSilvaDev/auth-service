from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.dependencies import get_current_user
from auth_service.db.session import get_db
from auth_service.modules.auth.models import User
from auth_service.modules.auth.repository import (
    RefreshTokenRepository,
    TokenTypeRepository,
    UserRepository,
    UserTokenVerificationRepository,
)
from auth_service.modules.auth.schemas import (
    RefreshRequest,
    UserCreate,
    UserLogin,
    UserLoginReturn,
    UserRefreshToken,
    UserResponse,
    ValidateAccount,
)
from auth_service.modules.auth.service import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_db)]
Current_User = Annotated[User, Depends(get_current_user)]


@router.post(
    '/register', response_model=UserResponse, status_code=HTTPStatus.CREATED
)
async def register_user(data: UserCreate, db: Session):

    service = AuthService(
        repository=UserRepository(db),
        tokenTypeRepository=TokenTypeRepository(db),
        userVerificationTokenRepository=UserTokenVerificationRepository(db),
    )
    try:
        user = await service.register(data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post('/login', response_model=UserLoginReturn)
async def login(data: UserLogin, db: Session):
    service = AuthService(
        repository=UserRepository(db),
        refreshRepository=RefreshTokenRepository(db),
    )
    try:
        result = await service.login(data)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get('/me', response_model=UserResponse)
async def me(current_user: Current_User):
    return current_user


@router.post('/refresh', response_model=UserRefreshToken)
async def refresh(data: RefreshRequest, db: Session):
    service = AuthService(UserRepository(db), RefreshTokenRepository(db))

    try:
        return await service.refresh(data.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
        )


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: RefreshRequest, db: Session):
    service = AuthService(UserRepository(db), RefreshTokenRepository(db))

    await service.logout(data.refresh_token)


@router.post('/validate-account', status_code=status.HTTP_204_NO_CONTENT)
async def validate_account(data: ValidateAccount, db: Session):
    service = AuthService(
        repository=UserRepository(db),
        userVerificationTokenRepository=UserTokenVerificationRepository(db),
    )

    try:
        await service.validate_account(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
