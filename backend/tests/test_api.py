import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health_endpoint(client: AsyncClient):
    res = await client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "documents_count" in data


@pytest.mark.anyio
async def test_register_and_login(client: AsyncClient):
    res = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "name": "Test User", "password": "testpass123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["email"] == "test@example.com"

    res = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    assert res.status_code == 200
    assert "token" in res.json()


@pytest.mark.anyio
async def test_login_invalid_credentials(client: AsyncClient):
    res = await client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    assert res.status_code == 401


@pytest.mark.anyio
async def test_search_no_documents(client: AsyncClient):
    res = await client.post(
        "/api/search",
        json={"query": "test query", "top_k": 3},
    )
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "sources" in data


@pytest.mark.anyio
async def test_chat_creates_conversation(client: AsyncClient):
    res = await client.post(
        "/api/chat",
        json={"query": "What is diabetes?", "top_k": 3},
    )
    assert res.status_code == 200
    data = res.json()
    assert "conversation_id" in data
    assert "answer" in data


@pytest.mark.anyio
async def test_conversations_list(client: AsyncClient):
    res = await client.get("/api/conversations")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.anyio
async def test_ingest_validation(client: AsyncClient):
    res = await client.post(
        "/api/ingest",
        json={"query": "", "max_results": 0},
    )
    assert res.status_code == 422
