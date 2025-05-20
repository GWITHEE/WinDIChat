import pytest
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_websocket_flow(client):
    # Test WebSocket connection and message flow
    async with client.websocket_connect("/ws/1") as websocket:
        await websocket.send_json({"text": "Hello World"})
        response = await websocket.receive_json()
        assert response["text"] == "Hello World"
