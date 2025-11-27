from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories import MessageRepository
from ..models import Message


class MessageService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MessageRepository(db)

    def send_message(self, payload: Dict[str, Any]) -> Message:
        required = ("content", "subchannelId", "authorId")
        if not all(payload.get(k) for k in required):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados incompletos para enviar mensagem")

        msg = self.repo.create(payload)
        return msg

    def get_messages_in_subchannel(self, subchannel_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return self.repo.get_by_subchannel(subchannel_id, skip=skip, limit=limit)

    def delete_message(self, message_id: int) -> bool:
        return self.repo.delete(message_id)
