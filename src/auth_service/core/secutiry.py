from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from auth_service.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(
    subject: str, token_type: str, expires_delta: timedelta
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta

    payload = {'sub': str(subject), 'type': token_type, 'exp': expire}

    token = jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )

    return token, expire


def create_access_token(user_id: int) -> str:
    token, _ = create_token(
        user_id,
        'access',
        timedelta(minutes=settings.access_token_expire_minutes),
    )

    return token


def create_refresh_token(user_id: int) -> str:
    token, expire = create_token(
        user_id, 'refresh', timedelta(days=settings.refresh_token_expire_days)
    )

    return token, expire


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise ValueError('Invalid token')
