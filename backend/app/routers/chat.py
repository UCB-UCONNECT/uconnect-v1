from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime

from ..models import Conversation, Channel, Subchannel, Message, User, ConversationType
from ..schemas import Chat, Message as MessageSchema, MessageCreate, UserSimple, ChatCreate
from .. import utils, models, schemas
from ..db.session import get_db
from ..dependencies import get_current_user
from ..services import ConversationService, MessageService
from .notifications import notify_new_message


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(db)


def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    return MessageService(db)

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/", response_model=List[schemas.Chat])
@router.get("/conversations", response_model=List[schemas.Chat])
def get_user_conversations(
    conversation_service: ConversationService = Depends(get_conversation_service),
    message_service: MessageService = Depends(get_message_service),
    current_user: models.User = Depends(get_current_user)
):
    user_chats = conversation_service.list_by_participant(current_user.id)

    result = []
    for chat in user_chats:
        channel = conversation_service.db.query(models.Channel).filter(
            models.Channel.conversationId == chat.id
        ).first()

        last_msg_schema = None
        if channel:
            subchannel = db.query(models.Subchannel).filter(
                models.Subchannel.parentChannelId == channel.id
            ).first()

            if subchannel:
                last_row = (
                    message_service.db.query(models.Message, models.User.name.label("author_name"))
                    .join(models.User, models.User.id == models.Message.authorId, isouter=True)
                    .filter(models.Message.subchannelId == subchannel.id)
                    .order_by(desc(models.Message.timestamp))
                    .limit(1)
                    .one_or_none()
                )

                if last_row is not None:
                    last_msg, author_name = last_row
                    last_msg_schema = schemas.Message(
                        id=last_msg.id,
                        content=last_msg.content,
                        timestamp=last_msg.timestamp,
                        authorId=last_msg.authorId,
                        authorName=author_name
                    )

        chat_data = schemas.Chat(
            id=chat.id,
            title=chat.title or "Sem título",
            participants=[schemas.UserSimple(id=p.id, name=p.name) for p in chat.participants],
            last_message=last_msg_schema
        )
        result.append(chat_data)

    return result

@router.get("/{chat_id}/messages", response_model=List[schemas.Message])
def get_chat_messages(
    chat_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service),
    message_service: MessageService = Depends(get_message_service),
    current_user: models.User = Depends(get_current_user)
):
    chat = conversation_service.get_conversation(chat_id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    channel = conversation_service.db.query(models.Channel).filter(models.Channel.conversationId == chat_id).first()
    if not channel:
        return []
    subchannel = conversation_service.db.query(models.Subchannel).filter(models.Subchannel.parentChannelId == channel.id).first()
    if not subchannel:
        return []

    rows = (
        message_service.db.query(models.Message, models.User.name.label("author_name"))
        .join(models.User, models.User.id == models.Message.authorId, isouter=True)
        .filter(models.Message.subchannelId == subchannel.id)
        .order_by(models.Message.timestamp.asc())
        .all()
    )

    messages = [
        schemas.Message(
            id=m.id,
            content=m.content,
            timestamp=m.timestamp,
            authorId=m.authorId,
            authorName=author_name
        )
        for (m, author_name) in rows
    ]

    message_service.db.query(models.Message).filter(
        models.Message.subchannelId == subchannel.id,
        models.Message.authorId != current_user.id,
        models.Message.isRead == False
    ).update({"isRead": True})
    message_service.db.commit()

    return messages

@router.post("/{chat_id}/messages", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(
    chat_id: int,
    message: schemas.MessageCreate,
    conversation_service: ConversationService = Depends(get_conversation_service),
    message_service: MessageService = Depends(get_message_service),
    current_user: models.User = Depends(get_current_user)
):
    chat = conversation_service.get_conversation(chat_id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    channel = conversation_service.db.query(models.Channel).filter(models.Channel.conversationId == chat_id).first()
    if not channel:
        channel = models.Channel(name=f"Channel-{chat_id}", conversationId=chat_id)
        conversation_service.db.add(channel)
        conversation_service.db.flush()

    subchannel = conversation_service.db.query(models.Subchannel).filter(models.Subchannel.parentChannelId == channel.id).first()
    if not subchannel:
        subchannel = models.Subchannel(name="Geral", parentChannelId=channel.id)
        conversation_service.db.add(subchannel)
        conversation_service.db.flush()

    payload = {
        "content": message.content,
        "subchannelId": subchannel.id,
        "authorId": current_user.id,
        "timestamp": datetime.utcnow(),
        "isRead": False
    }
    new_message = message_service.send_message(payload)
    chat.updatedAt = datetime.utcnow()
    conversation_service.db.commit()
    message_service.db.refresh(new_message)

    await notify_new_message(chat_id, current_user.id, message.content, message_service.db)

    return schemas.Message(
        id=new_message.id,
        content=new_message.content,
        timestamp=new_message.timestamp,
        authorId=new_message.authorId,
        authorName=current_user.name
    )

@router.post("/{chat_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_messages_as_read(
    chat_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service),
    message_service: MessageService = Depends(get_message_service),
    current_user: models.User = Depends(get_current_user)
):
    conversation = conversation_service.get_conversation(chat_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in conversation.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    channel = conversation_service.db.query(models.Channel).filter(models.Channel.conversationId == chat_id).first()
    if not channel:
        return

    subchannel = conversation_service.db.query(models.Subchannel).filter(models.Subchannel.parentChannelId == channel.id).first()
    if not subchannel:
        return

    message_service.db.query(models.Message).filter(
        models.Message.subchannelId == subchannel.id,
        models.Message.authorId != current_user.id,
        models.Message.isRead == False
    ).update({"isRead": True})

    message_service.db.commit()
    return

@router.post("/", response_model=schemas.Chat, status_code=status.HTTP_201_CREATED)
def create_conversation(
    chat_data: schemas.ChatCreate,
    conversation_service: ConversationService = Depends(get_conversation_service),
    current_user: models.User = Depends(get_current_user)
):
    participants = conversation_service.db.query(models.User).filter(models.User.id.in_(chat_data.participant_ids)).all()

    if len(participants) != len(chat_data.participant_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participantes não encontrados")

    if current_user not in participants:
        participants.append(current_user)

    if chat_data.title and chat_data.title.strip():
        title = chat_data.title.strip()
    else:
        others = [p.name for p in participants if p.id != current_user.id]
        title = f"Chat com {', '.join(others)}" if others else "Chat"

    conv_type = models.ConversationType.direct if len(participants) == 2 else models.ConversationType.group

    new_conversation = models.Conversation(title=title, type=conv_type, participants=participants)
    conversation_service.db.add(new_conversation)
    conversation_service.db.flush()

    channel = models.Channel(name=f"Channel-{new_conversation.id}", conversationId=new_conversation.id)
    conversation_service.db.add(channel)
    conversation_service.db.flush()

    subchannel = models.Subchannel(name="Geral", parentChannelId=channel.id)
    conversation_service.db.add(subchannel)
    conversation_service.db.commit()
    conversation_service.db.refresh(new_conversation)

    return schemas.Chat(
        id=new_conversation.id,
        title=new_conversation.title,
        participants=[schemas.UserSimple(id=p.id, name=p.name) for p in participants],
        last_message=None
    )

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    chat_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service),
    current_user: models.User = Depends(get_current_user)
):
    conversation = conversation_service.get_conversation(chat_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")

    participant_ids = [p.id for p in conversation.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    success = conversation_service.delete_conversation(chat_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao deletar conversa")
    return
