# FastAPI Boilerplate

Boilerplate para projetos FastAPI com autenticação JWT, banco de dados PostgreSQL, e estrutura de testes completamente configurada.

## Características

- ✅ **FastAPI** - Framework moderno e de alta performance para APIs REST
- ✅ **SQLAlchemy 2.0** - ORM assíncrono com suporte a tipagem
- ✅ **JWT Authentication** - Sistema completo de autenticação e renovação de tokens
- ✅ **PostgreSQL** - Suporte nativo ao PostgreSQL usando Psycopg
- ✅ **Alembic** - Gerenciamento de migrações do banco de dados
- ✅ **Docker** - Containerização completa da aplicação
- ✅ **Poetry** - Gerenciamento de dependências
- ✅ **Pytest** - Suite de testes abrangente com fixtures predefinidas
- ✅ **Testcontainers** - Testes de integração isolados
- ✅ **Ruff** - Linting e formatação de código
- ✅ **Argon2** - Hashing seguro de senhas com pwdlib

## Requisitos

- Python 3.12+
- Docker & Docker Compose
- Poetry

## Início Rápido

### 1. Clone o repositório

```bash
git clone https://github.com/yourusername/fastapi-boilerplate.git
cd fastapi-boilerplate
```

### 2. Configure o ambiente

Crie um arquivo .env baseado no .env.example:

```bash
cp .env.example .env
```

Crie um arquivo docker-compose.yml baseado no docker-compose.yml.example

```bash
cp docker-compose.yml.example docker-compose.yml
```

Atualize as variáveis de ambiente no arquivo .env:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=myapp
DB_URL=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

SECRET_KEY="sua-chave-secreta-aqui"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Execute a aplicação

```bash
docker compose up -d
```

A API estará disponível em `http://localhost:8000`

## Desenvolvimento

### Crie ou ative uma máquina virtual

```bash
poetry env activate
```

### Instale as dependências
```bash
poetry install
```

### Rode o docker compose
O método recomendado para desenvolvimento é usar Docker Compose, que já configura todo o ambiente necessário:

```bash
docker compose up -d
```

Para acompanhar os logs da aplicação:

```bash
docker compose logs -f app
```

Para reiniciar a aplicação após alterações:

```bash
docker compose restart app
```

### Migrações

Acesse um bash dentro do container ``app``:
```bash
docker compose exec app bash
```

Para analisar migrações:
```bash
# Dentro do container:
alembic revision --autogenerate -m "mensagem-da-migracao-aqui" #um arquivo será gerado na pasta alembic/versions
```

Para executar migrações:
```bash
# Dentro do container:
alembic upgrade head
```

### Executar testes

```bash
poetry run task test
```

O comando acima executa os testes com cobertura de código e gera um relatório HTML.

### Lint e formatação de código

```bash
poetry run task lint     # verificar código
poetry run task format   # formatar código automático
```

## Autenticação

Esta API usa autenticação baseada em token JWT. Os tokens expiram após 30 minutos (configurável).

### Obter token

```bash
curl -X POST http://localhost:8000/auth/token \
  -d "username=user@example.com" \
  -d "password=secretpassword"
```

### Renovar token antes da expiração

```bash
curl -X POST http://localhost:8000/auth/refresh_token \
  -H "Authorization: Bearer seu_token_aqui"
```

## Endpoints da API

- `/` - Endpoint de saúde da API
- `/auth/token` - Obter token de acesso
- `/auth/refresh_token` - Renovar token de acesso
- `/users/` - CRUD de usuários

A documentação da API está disponível em ``http://localhost:8000/docs``

## Detalhes Técnicos

- **SQLAlchemy**: Configurado com suporte a operações assíncronas
- **Pydantic v2**: Para validação de dados e configurações
- **PWDLib com Argon2**: Para hashing seguro de senhas
- **Test Concurrency**: Suporte para threading e greenlet durante os testes

## Licença

MIT
