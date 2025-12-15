from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.db.session import get_db
from auth_service.modules.auth.repository import UserRepository
from auth_service.modules.auth.schemas import UserCreate, UserResponse
from auth_service.modules.auth.service import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    '/register', response_model=UserResponse, status_code=HTTPStatus.CREATED
)
async def register_user(data: UserCreate, db: Session):

    service = AuthService(UserRepository(db))
    try:
        user = await service.register(data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
