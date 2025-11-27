from typing import List
from sqlalchemy.orm import Session
from .base import GenericRepository
from ..models import Announcement


class AnnouncementRepository(GenericRepository[Announcement]):
    """Repositório para anúncios/comunicados."""

    def __init__(self, db: Session):
        super().__init__(db, Announcement)

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100):
        return self.find_all_by_filter(skip=skip, limit=limit, authorId=author_id)
