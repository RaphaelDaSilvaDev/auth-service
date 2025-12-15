from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.secutiry import decode_token
from auth_service.db.session import get_db
from auth_service.modules.auth.repository import UserRepository
from auth_service.modules.auth.schemas import UserResponse

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login')


async def get_current_user(
    token: str = Depends(oauth2_schema), db: AsyncSession = Depends(get_db)
) -> UserResponse:
    try:
        payload = decode_token(token)
        if payload.get('type') != 'access':
            raise ValueError()
        user_id = int(payload.get('sub'))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
        )

    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found'
        )

    return user
