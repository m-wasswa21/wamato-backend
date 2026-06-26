import uuid
from typing import List
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import decode_token
from app.schemas.message import ConversationCreate, MessageCreate, MessageOut, ConversationOut
from app.schemas.common import Paginated
from app.services.message import MessageService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/messages", tags=["Messages"])

# In-memory connection manager (swap for Redis pub/sub in production)
class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, conversation_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(conversation_id, []).append(ws)

    def disconnect(self, conversation_id: str, ws: WebSocket):
        conns = self.active.get(conversation_id, [])
        if ws in conns:
            conns.remove(ws)

    async def broadcast(self, conversation_id: str, data: dict):
        for ws in self.active.get(conversation_id, []):
            try:
                await ws.send_json(data)
            except Exception:
                pass


manager = ConnectionManager()


@router.post("/conversations", response_model=ConversationOut, status_code=201)
async def start_conversation(
    body: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MessageService.get_or_create_conversation(db, current_user.id, body)


@router.get("/conversations", response_model=List[ConversationOut])
async def my_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    convs = await MessageService.get_user_conversations(db, current_user.id)
    result = []
    for c in convs:
        d = ConversationOut.model_validate(c)
        d.participant_a_name = getattr(c, "participant_a_name", None)
        d.participant_b_name = getattr(c, "participant_b_name", None)
        result.append(d)
    return result


@router.get("/conversations/{conv_id}/messages", response_model=Paginated[MessageOut])
async def get_messages(
    conv_id: uuid.UUID,
    page: int = 1,
    size: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await MessageService.get_messages(db, conv_id, current_user.id, page, size)


@router.post("/conversations/{conv_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
    conv_id: uuid.UUID,
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    msg = await MessageService.send(db, conv_id, body, current_user.id)
    await manager.broadcast(str(conv_id), {"event": "new_message", "data": msg.model_dump(mode="json")})
    return msg


@router.websocket("/ws/{conv_id}")
async def websocket_endpoint(conv_id: str, ws: WebSocket, token: str = ""):
    payload = decode_token(token)
    if not payload:
        await ws.close(code=4001)
        return
    await manager.connect(conv_id, ws)
    try:
        while True:
            await ws.receive_text()  # keepalive — messages sent via REST
    except WebSocketDisconnect:
        manager.disconnect(conv_id, ws)
