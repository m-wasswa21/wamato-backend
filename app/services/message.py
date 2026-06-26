import uuid
import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models.message import Conversation, Message
from app.schemas.message import ConversationCreate, MessageCreate, MessageOut
from app.schemas.common import Paginated
from app.core.exceptions import NotFound, Forbidden


class MessageService:

    @staticmethod
    async def get_or_create_conversation(
        db: AsyncSession, user_id: uuid.UUID, body: ConversationCreate
    ) -> Conversation:
        res = await db.execute(
            select(Conversation).where(
                or_(
                    (Conversation.participant_a == user_id) & (Conversation.participant_b == body.recipient_id),
                    (Conversation.participant_a == body.recipient_id) & (Conversation.participant_b == user_id),
                )
            )
        )
        conv = res.scalar_one_or_none()
        if conv is None:
            conv = Conversation(
                participant_a=user_id,
                participant_b=body.recipient_id,
                property_id=body.property_id,
                last_message_preview=body.first_message[:100],
            )
            db.add(conv)
            await db.flush()

            msg = Message(
                conversation_id=conv.id,
                sender_id=user_id,
                content=body.first_message,
            )
            db.add(msg)
            await db.flush()

        return conv

    @staticmethod
    async def get_user_conversations(db: AsyncSession, user_id: uuid.UUID) -> list:
        res = await db.execute(
            select(Conversation)
            .where(or_(Conversation.participant_a == user_id, Conversation.participant_b == user_id))
            .options(selectinload(Conversation.user_a), selectinload(Conversation.user_b))
            .order_by(Conversation.updated_at.desc())
        )
        convs = res.scalars().all()
        # Attach participant names for the client
        for c in convs:
            c.participant_a_name = c.user_a.full_name if c.user_a else None
            c.participant_b_name = c.user_b.full_name if c.user_b else None
        return convs

    @staticmethod
    async def get_messages(
        db: AsyncSession, conv_id: uuid.UUID, user_id: uuid.UUID, page: int, size: int
    ) -> Paginated:
        conv = await db.execute(select(Conversation).where(Conversation.id == conv_id))
        c = conv.scalar_one_or_none()
        if not c:
            raise NotFound("Conversation")
        if user_id not in (c.participant_a, c.participant_b):
            raise Forbidden()

        total_res = await db.execute(
            select(func.count()).select_from(Message).where(Message.conversation_id == conv_id)
        )
        total = total_res.scalar_one()
        offset = (page - 1) * size
        res = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at.asc())
            .offset(offset).limit(size)
        )
        items = res.scalars().all()
        return Paginated(items=items, total=total, page=page, size=size, pages=math.ceil(total / size) if total else 0)

    @staticmethod
    async def send(
        db: AsyncSession, conv_id: uuid.UUID, body: MessageCreate, sender_id: uuid.UUID
    ) -> MessageOut:
        conv_res = await db.execute(select(Conversation).where(Conversation.id == conv_id))
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise NotFound("Conversation")
        if sender_id not in (conv.participant_a, conv.participant_b):
            raise Forbidden()

        msg = Message(conversation_id=conv_id, sender_id=sender_id, **body.model_dump())
        db.add(msg)
        conv.last_message_preview = body.content[:100]
        db.add(conv)
        await db.flush()
        await db.refresh(msg)
        return MessageOut.model_validate(msg)
