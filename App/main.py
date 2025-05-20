from fastapi import FastAPI, WebSocket, Depends, HTTPException
from .auth import get_current_user
from .websocket_manager import manager
from .models import User, Chat, Message
from .database import AsyncSessionLocal
from sqlalchemy.future import select
import json
import os

app = FastAPI()

# WebSocket endpoint
@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    current_user: dict = Depends(get_current_user)
):
    await manager.connect(websocket, chat_id, current_user["user_id"])
    try:
        while True:
            data = await websocket.receive_json()
            async with AsyncSessionLocal() as session:
                msg = Message(
                    chat_id=chat_id,
                    sender_id=current_user["user_id"],
                    text=data["text"],
                    is_read=False
                )
                session.add(msg)
                await session.commit()
                await session.refresh(msg)
                
            await manager.broadcast(chat_id, {
                "id": msg.id,
                "chat_id": chat_id,
                "sender_id": current_user["user_id"],
                "text": data["text"],
                "timestamp": msg.timestamp.isoformat(),
                "is_read": False
            })
            
            await manager.store_message({
                "chat_id": chat_id,
                "message_id": msg.id,
                "content": data["text"],
                "sender": current_user["user_id"],
                "timestamp": msg.timestamp.isoformat()
            })
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# REST endpoints
@app.get("/history/{chat_id}")
async def get_history(
    chat_id: int,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        messages = result.scalars().all()
        return [{
            "id": msg.id,
            "chat_id": msg.chat_id,
            "sender_id": msg.sender_id,
            "text": msg.text,
            "timestamp": msg.timestamp.isoformat(),
            "is_read": msg.is_read
        } for msg in messages]

# Additional endpoints for auth, groups etc...
