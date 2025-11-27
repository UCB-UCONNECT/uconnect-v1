from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories import ConversationRepository
from ..models import Conversation, User


class ConversationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ConversationRepository(db)

    def create_conversation(self, payload: Dict[str, Any]) -> Conversation:
        if not payload.get("type"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de conversa é obrigatório")

        conv = self.repo.create(payload)
        return conv

    def get_conversation(self, conv_id: int) -> Optional[Conversation]:
        return self.repo.get_by_id(conv_id)

    def list_by_participant(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Conversation]:
        return self.repo.get_by_participant(user_id, skip=skip, limit=limit)

    def update_conversation(self, conv_id: int, data: Dict[str, Any]) -> Optional[Conversation]:
        return self.repo.update(conv_id, data)

    def delete_conversation(self, conv_id: int) -> bool:
        return self.repo.delete(conv_id)
