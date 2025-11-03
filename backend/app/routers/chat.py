# ---------------- ROTAS DE CHAT (VERSÃO COMPATÍVEL) ---------------- #
"""
Rotas de chat ajustadas para a estrutura:
Conversation → Channel → Subchannel → Message
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime

from .. import models, schemas, utils
from ..db import get_db

router = APIRouter(
    prefix="/chats",
    tags=["Chat"]
)

# Dependência para obter o usuário logado
get_current_user = utils.get_current_user


@router.get("/", response_model=List[schemas.Chat])
def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Lista todas as conversas das quais o usuário atual participa.
    """
    # Busca todas as conversas em que o usuário atual é um participante
    user_chats = db.query(models.Conversation).filter(
        models.Conversation.participants.any(id=current_user.id)
    ).all()

    result = []
    for chat in user_chats:
        # Encontra o channel associado à conversa
        channel = db.query(models.Channel).filter(
            models.Channel.conversationId == chat.id
        ).first()

        last_msg_schema = None
        if channel:
            # Se um channel for encontrado, busca o subchannel
            subchannel = db.query(models.Subchannel).filter(
                models.Subchannel.parentChannelId == channel.id
            ).first()

            if subchannel:
                # Busca a mensagem mais recente com JOIN no autor
                last_row = (
                    db.query(
                        models.Message,
                        models.User.name.label("author_name")
                    )
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

        # Cria objeto para resposta
        chat_data = schemas.Chat(
            id=chat.id,
            title=chat.title or "Sem título",
            participants=[
                schemas.UserSimple(id=p.id, name=p.name)
                for p in chat.participants
            ],
            last_message=last_msg_schema
        )
        result.append(chat_data)

    return result


@router.get("/{chat_id}/messages", response_model=List[schemas.Message])
def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtém todas as mensagens de uma conversa específica.
    """
    # Validação 1: A conversa existe?
    chat = db.query(models.Conversation).filter(
        models.Conversation.id == chat_id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )

    # Validação 2: O usuário atual pertence a esta conversa?
    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a esta conversa"
        )

    # Encontra o channel da conversa
    channel = db.query(models.Channel).filter(
        models.Channel.conversationId == chat_id
    ).first()
    if not channel:
        return []

    # Encontra o subchannel do channel
    subchannel = db.query(models.Subchannel).filter(
        models.Subchannel.parentChannelId == channel.id
    ).first()
    if not subchannel:
        return []

    # Busca todas as mensagens com o nome do autor (JOIN)
    rows = (
        db.query(
            models.Message,
            models.User.name.label("author_name")
        )
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

    # Marca como lidas (exceto as do próprio usuário)
    db.query(models.Message).filter(
        models.Message.subchannelId == subchannel.id,
        models.Message.authorId != current_user.id,
        models.Message.isRead == False
    ).update({"isRead": True})
    db.commit()

    return messages


@router.post("/{chat_id}/messages", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(
    chat_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Envia uma nova mensagem para uma conversa.
    """
    # Validações de segurança
    chat = db.query(models.Conversation).filter(
        models.Conversation.id == chat_id
    ).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )

    participant_ids = [p.id for p in chat.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode enviar mensagens para esta conversa"
        )

    # Encontra ou cria o channel
    channel = db.query(models.Channel).filter(
        models.Channel.conversationId == chat_id
    ).first()
    if not channel:
        channel = models.Channel(
            name=f"Channel-{chat_id}",
            conversationId=chat_id
        )
        db.add(channel)
        db.flush()

    # Encontra ou cria o subchannel
    subchannel = db.query(models.Subchannel).filter(
        models.Subchannel.parentChannelId == channel.id
    ).first()
    if not subchannel:
        subchannel = models.Subchannel(
            name="Geral",
            parentChannelId=channel.id
        )
        db.add(subchannel)
        db.flush()

    # Cria a nova mensagem
    new_message = models.Message(
        content=message.content,
        subchannelId=subchannel.id,
        authorId=current_user.id,
        timestamp=datetime.utcnow(),
        isRead=False
    )
    db.add(new_message)

    # Atualiza o timestamp da conversa
    chat.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(new_message)

    # Retorna já com o nome do autor (o do usuário atual)
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Marca todas as mensagens de uma conversa (que não foram enviadas pelo usuário atual) como lidas.
    """
    # Validações de segurança
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == chat_id
    ).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )

    participant_ids = [p.id for p in conversation.participants]
    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a esta conversa"
        )

    # Encontra o channel
    channel = db.query(models.Channel).filter(
        models.Channel.conversationId == chat_id
    ).first()
    if not channel:
        return

    # Encontra o subchannel
    subchannel = db.query(models.Subchannel).filter(
        models.Subchannel.parentChannelId == channel.id
    ).first()
    if not subchannel:
        return

    # Atualiza o status 'isRead' das mensagens
    db.query(models.Message).filter(
        models.Message.subchannelId == subchannel.id,
        models.Message.authorId != current_user.id,
        models.Message.isRead == False
    ).update({"isRead": True})

    db.commit()
    return


@router.post("/", response_model=schemas.Chat, status_code=status.HTTP_201_CREATED)
def create_conversation(
    chat_data: schemas.ChatCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cria uma nova conversa entre usuários.
    """
    # Buscar participantes
    participants = db.query(models.User).filter(
        models.User.id.in_(chat_data.participant_ids)
    ).all()

    if len(participants) != len(chat_data.participant_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um ou mais participantes não foram encontrados"
        )

    # Adicionar o usuário atual se não estiver na lista
    if current_user not in participants:
        participants.append(current_user)

    # Definir título
    if chat_data.title and chat_data.title.strip():
        title = chat_data.title.strip()
    else:
        others = [p.name for p in participants if p.id != current_user.id]
        title = f"Chat com {', '.join(others)}" if others else "Chat"

    # Tipo de conversa
    conv_type = models.ConversationType.direct if len(participants) == 2 else models.ConversationType.group

    # Criar a conversa
    new_conversation = models.Conversation(
        title=title,
        type=conv_type,
        participants=participants
    )
    db.add(new_conversation)
    db.flush()

    # Criar channel automaticamente
    channel = models.Channel(
        name=f"Channel-{new_conversation.id}",
        conversationId=new_conversation.id
    )
    db.add(channel)
    db.flush()

    # Criar subchannel automaticamente
    subchannel = models.Subchannel(
        name="Geral",
        parentChannelId=channel.id
    )
    db.add(subchannel)
    db.commit()
    db.refresh(new_conversation)

    return schemas.Chat(
        id=new_conversation.id,
        title=new_conversation.title,
        participants=[schemas.UserSimple(id=p.id, name=p.name) for p in participants],
        last_message=None
    )