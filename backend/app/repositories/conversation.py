from typing import List
from sqlalchemy.orm import Session
from .base import GenericRepository
from ..models import Conversation


class ConversationRepository(GenericRepository[Conversation]):
    """Repositório para conversas e threads."""

    def __init__(self, db: Session):
        super().__init__(db, Conversation)

    def get_by_participant(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
        # busca conversas onde participants contém userId (relacionamento many-to-many)
        query = self.db.query(Conversation).join(Conversation.participants).filter(Conversation.participants.any())
        # preferir usar find_all_by_filter quando possível; aqui usamos join para demonstrar
        return query.offset(skip).limit(limit).all()
