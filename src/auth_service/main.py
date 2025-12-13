from fastapi import FastAPI

from auth_service.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get('/')
def health_check():
    return {'status': 'ok'}
