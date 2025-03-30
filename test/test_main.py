import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, engine
from app.models import Base, User, Task
from app.auth import get_password_hash, create_access_token
import asyncio

# Configuração do banco de teste
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/test_tasks"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

# Sobrescreve a dependência do banco para usar o banco de teste
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    # Cria as tabelas no banco de teste
    async def setup_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(setup_db())
    return TestClient(app)

@pytest.fixture
async def test_db():
    async with TestSessionLocal() as session:
        yield session
        # Limpa os dados após cada teste
        await session.execute("DELETE FROM tasks")
        await session.execute("DELETE FROM users")
        await session.commit()

@pytest.fixture
async def test_user(test_db: AsyncSession):
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpassword")
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user: User):
    token = create_access_token({"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

def test_create_user(client: TestClient):
    response = client.post(
        "/users",
        json={"username": "newuser", "password": "newpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data

def test_login(client: TestClient, test_user: User):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_and_get_task(client: TestClient, auth_headers: dict, test_user: User):
    # Criar uma tarefa
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "description": "Test Description"},
        headers=auth_headers
    )
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Test Task"
    assert task["status"] == "pending"
    assert task["owner_id"] == test_user.id

    # Obter a tarefa criada
    task_id = task["id"]
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

def test_update_and_delete_task(client: TestClient, auth_headers: dict, test_user: User):
    # Criar uma tarefa primeiro
    response = client.post(
        "/tasks",
        json={"title": "Initial", "description": "Desc"},
        headers=auth_headers
    )
    task_id = response.json()["id"]

    # Testar atualização
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated", "description": "New Desc", "status": "done"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "done"

    # Testar deleção
    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verificar se foi deletada
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404

def test_unauthorized_access(client: TestClient):
    response = client.get("/tasks")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
