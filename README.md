# task-api

## Setup
1. Install Docker and Docker Compose
2. Build and run:
```bash
docker-compose up --build
```

Deployment to Render.com
Create a new Web Service on Render
Set repository URL
Configure:
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Add Environment Variable: DATABASE_URL
Add PostgreSQL instance via Render dashboard


Principais melhorias implementadas:

1. **Autenticação**
- JWT implementado com fastapi-security
- Rota /login que gera tokens
- Cada tarefa vinculada ao usuário via owner_id
- Proteção de endpoints com get_current_user

2. **PostgreSQL**
- Substituição do SQLite por PostgreSQL
- Uso de SQLAlchemy com asyncpg para operações assíncronas
- Arquitetura modular com models.py e database.py

3. **Containerização**
- Dockerfile para empacotar a API
- docker-compose.yml com serviços FastAPI + PostgreSQL
- Volume persistente para dados do banco

4. **Deploy**
- Configuração pronta para Render.com
- Pode ser adaptada para Fly.io ou Railway modificando os comandos de build/start
- Para VPS: usar Nginx como proxy reverso + Gunicorn como servidor WSGI

Para rodar localmente:
1. Instale Docker e Docker Compose
2. Execute `docker-compose up --build`
3. Acesse `http://localhost:8000/docs`

Para deploy no Render:
1. Crie um PostgreSQL instance
2. Configure o Web Service com o repositório
3. Adicione a variável DATABASE_URL
4. Faça deploy
