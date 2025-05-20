# WinDIChat
Реализация мессенджера на FastAPI, WebSocket, PostgreSQL и Docker.

## Запуск
```bash
docker-compose up --build
import websockets, asyncio
async def main():
    async with websockets.connect("ws://localhost:8000/ws/1") as ws:
        await ws.send("{\"text\": \"Test\"}")
        print(await ws.recv())
asyncio.run(main())

CREATE TABLE messages (id SERIAL PRIMARY KEY, text TEXT, timestamp TIMESTAMP DEFAULT NOW());

docker-compose exec backend python -c "from app.models import User; from app.auth import get_password_hash; from app.database import AsyncSessionLocal; import asyncio; async def main(): async with AsyncSessionLocal() as db: db.add(User(email='admin@windi.com', hashed_password=get_password_hash('P@ssw0rd!')); await db.commit(); asyncio.run(main())"
docker-compose logs -f backend
