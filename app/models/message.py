import uuid
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class MessageType(str, PyEnum):
    text = "text"
    image = "image"
    system = "system"


class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"

    property_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="SET NULL"))
    participant_a: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    participant_b: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_message_preview: Mapped[Optional[str]] = mapped_column(String(255))

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation", lazy="select", order_by="Message.created_at")
    user_a: Mapped["User"] = relationship("User", foreign_keys=[participant_a])
    user_b: Mapped["User"] = relationship("User", foreign_keys=[participant_b])


class Message(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(Enum(MessageType), default=MessageType.text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    attachment_url: Mapped[Optional[str]] = mapped_column(String(512))

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
