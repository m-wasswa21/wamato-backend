import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.message import MessageType


class ConversationCreate(BaseModel):
    recipient_id: uuid.UUID
    property_id: Optional[uuid.UUID] = None
    first_message: str


class MessageCreate(BaseModel):
    content: str
    message_type: MessageType = MessageType.text
    attachment_url: Optional[str] = None


class MessageOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    message_type: MessageType
    is_read: bool
    attachment_url: Optional[str]
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    property_id: Optional[uuid.UUID]
    participant_a: uuid.UUID
    participant_b: uuid.UUID
    last_message_preview: Optional[str]
    updated_at: datetime
