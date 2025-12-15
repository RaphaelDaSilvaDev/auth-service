from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth_service.core.config import settings
from auth_service.db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    from auth_service.db.session import engine  # noqa: PLC0415

    print('🚀 Iniciando a aplicação: Conectando ao Banco de Dados...')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print('🛑 Encerrando a aplicação: Fechando conexões...')


app = FastAPI(title=settings.app_name, lifespan=lifespan)

from auth_service.modules.auth.router import router as auth_router  # noqa: E402, I001

app.include_router(auth_router)
