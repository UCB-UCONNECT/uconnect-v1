from typing import List
from sqlalchemy.orm import Session
from .base import GenericRepository
from ..models import Message


class MessageRepository(GenericRepository[Message]):
    """Repositório para mensagens dentro de subchannels."""

    def __init__(self, db: Session):
        super().__init__(db, Message)

    def get_by_subchannel(self, subchannel_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return self.find_all_by_filter(skip=skip, limit=limit, subchannelId=subchannel_id)

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return self.find_all_by_filter(skip=skip, limit=limit, authorId=author_id)
