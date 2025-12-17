from datetime import datetime, timedelta, timezone

from auth_service.core.security.codes import generate_numeric_code
from auth_service.core.secutiry import hash_password
from auth_service.infra.rabbitmq.publisher import publish_email_event
from auth_service.modules.auth.repository import (
    TokenTypeRepository,
    UserTokenVerificationRepository,
)
from auth_service.modules.auth.schemas import (
    UserCreatedEvent,
    VerifyEmailRabbitMQ,
)


class SendEmailVerificationHandle:
    def __init__(
        self,
        tokenTypeRepository: TokenTypeRepository,
        userVerificationTokenRepository: UserTokenVerificationRepository,
    ):
        self.tokenTypeRepository = tokenTypeRepository
        self.userVerificationTokenRepository = userVerificationTokenRepository

    async def handle(self, event: UserCreatedEvent):
        token_type = await self.tokenTypeRepository.get_by_name('verify_email')

        if not token_type:
            raise ValueError('Token type not found')

        verification_code = generate_numeric_code()

        await self.userVerificationTokenRepository.create(
            user_id=event.user_id,
            code=hash_password(verification_code),
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=token_type.expires_in_minutes),
            token_type_id=token_type.id,
        )

        payload_email = VerifyEmailRabbitMQ(
            code=verification_code,
            email=event.email,
            name=event.username,
            type=token_type.name,
        )

        await publish_email_event(payload_email.model_dump())
