import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    type: NotificationType
    title: str
    body: str
    is_read: bool
    action_url: Optional[str]
    related_id: Optional[str]
    created_at: datetime
