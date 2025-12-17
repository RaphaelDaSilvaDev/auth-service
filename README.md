# Auth Service

Este projeto implementa um serviço de autenticação moderno utilizando FastAPI, JWT, PostgreSQL, Docker e SQLAlchemy Async, seguindo boas práticas de arquitetura e segurança.

## 🚀 Stack
- Python 3.14
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker & Docker Compose
- JWT
- Pydantic
- Alembic
- RabbitMQ

**Este projeto se comunica com:** https://github.com/RaphaelDaSilvaDev/async_job_service  

## 📁 Estrutura do projeto
```text
auth_service/
├── core/ # Segurança, JWT, hashing, configurações
│ └── security/ # geração de código de verificação
├── db/ # Conexão e sessão com o banco
├── infra/
│ └── rabbitmq/ # criação do publisher
├── modules/
│ └── auth/
│    ├── handlers/
│    ├── models.py # Models SQLAlchemy
│    ├── schemas.py # Schemas Pydantic
│    ├── repository.py # Acesso a dados
│    ├── service.py # Regras de negócio
│    └── router.py # Rotas FastAPI
└── main.py
```
📌 Controllers (routers) não contêm regra de negócio.
📌 Services concentram toda a lógica de autenticação.
📌 Repositories lidam exclusivamente com persistência.

## 🔐 Fluxo de Autenticação
```text
1️⃣ Registro
Cria usuário com senha hasheada (bcrypt)
Valida e-mail único
Gera código para verificação de conta
Envia para fila RabbitMQ o email com o código 

2️⃣ Login
Valida credenciais
Valida conta ativa e verificada
Gera access token (JWT)
Gera refresh token (JWT)
Persiste o refresh token no banco

3️⃣ Access Token
Stateless
Curta duração
Usado para acessar rotas protegidas

4️⃣ Refresh Token
Stateful
Longa duração
Persistido no banco
Usado para renovar sessão

5️⃣ Refresh
Valida JWT
Valida tipo do token (refresh)
Verifica existência no banco
Verifica expiração
Retorna novo access token

6️⃣ Logout
Revoga o refresh token no banco
Access token expira naturalmente

7️⃣ Validação de conta
Valida email
Valida código de verificação

```
## 🔑 Rotas
```text
Método	Rota	Descrição
POST    /auth/register          # Registro de usuário
POST    /auth/login             # Login e geração de tokens
GET     /auth/me                # Dados do usuário autenticado
POST    /auth/refresh           # Gera novo access token
POST    /auth/logout            # Revoga refresh token
POST    /auth/validate-account  # Valida a conta com um código enviado por email
```

##🧪 Segurança
```text
Hash de senha com bcrypt
JWT assinado
Validação de tipo de token
Expiração controlada
Tokens sensíveis não armazenados em plaintext no client
Verificação de conta com código enviado por email
```

## ▶️ Executando o projeto
``` text
Requirements
* Docker
* Docker Compose
```

```text
# Subir containers (Aplicação e Banco de dados) e executar migrations
docker-compose up --build
```

```text
Api disponível em: http://localhost:8000
Documentação em: http://localhost:8000/docs
```
---
<div align="center">
Feito por Raphael da Silva 🚀 <br/>

</div>