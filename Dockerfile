FROM python:3.14-slim

WORKDIR app/

COPY . .

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --without dev

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.auth_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
