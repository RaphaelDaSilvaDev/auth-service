from fastapi import FastAPI

from auth_service.core.config import settings

app = FastAPI(title=settings.app_name)

from auth_service.modules.auth.router import router as auth_router  # noqa: E402, I001

app.include_router(auth_router)
