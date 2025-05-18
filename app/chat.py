# app/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from collections import defaultdict

router = APIRouter()
active_connections: dict[str, set[WebSocket]] = defaultdict(set)

def room_id(user_a: str, user_b: str) -> str:
    return "-".join(sorted([user_a, user_b]))

@router.websocket("/ws/{user}/{peer}")
async def chat_ws(ws: WebSocket, user: str, peer: str):
    await ws.accept()
    rid = room_id(user, peer)
    active_connections[rid].add(ws)
    try:
        while True:
            data = await ws.receive_text()
            # Diffuse à l’autre socket(s)
            for conn in list(active_connections[rid]):
                await conn.send_text(f"{user}:{data}")
    except WebSocketDisconnect:
        active_connections[rid].remove(ws)
