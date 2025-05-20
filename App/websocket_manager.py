import json
from fastapi import WebSocket
from aioredis import Redis

class ConnectionManager:
    def __init__(self):
        self.redis = Redis.from_url(os.getenv("REDIS_URL"))
        
    async def connect(self, websocket: WebSocket, chat_id: str, user_id: str):
        await websocket.accept()
        await self.redis.sadd(f"chat:{chat_id}:users", user_id)
        
    async def broadcast(self, chat_id: str, message: dict):
        users = await self.redis.smembers(f"chat:{chat_id}:users")
        for user in users:
            ws = await self.redis.get(f"user:{user}:ws")
            if ws:
                await ws.send_json(message)
                
    async def store_message(self, message: dict):
        await self.redis.xadd(f"chat:{message['chat_id']}:messages", message)
        
    async def get_message_history(self, chat_id: str, limit: int = 100, offset: int = 0):
        return await self.redis.xrange(f"chat:{chat_id}:messages", count=limit, start=offset)
    
manager = ConnectionManager()
