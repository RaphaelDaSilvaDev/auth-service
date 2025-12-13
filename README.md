# Auth Service

Servico de Autenticação desenvolvido com FastAPI, PostgresSQL e JWT, focando em arquitetura limpa e padrões de projeto.

## 🚀 Stack
- Python 3.14
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker & Docker Compose
- JWT

## 📁 Estrutura do projeto
```text
app/
 ├── core/        # Configurações, segurança, exceptions
 ├── db/          # Sessão e módulos base
 ├── modules/     # Módulos da aplicação (auth, users, etc.)
```
## ▶️ Executando o projeto
Requirements
* Docker
* Docker Compose

```text
docker-compose up --build
```