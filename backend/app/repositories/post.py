from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from .base import GenericRepository
from ..models import Post


class PostRepository(GenericRepository[Post]):
    """Repositório para Posts (Publications/Mural)."""

    def __init__(self, db: Session):
        super().__init__(db, Post)

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        return self.find_all_by_filter(skip=skip, limit=limit, authorId=author_id)

    def get_by_date(self, target_date: date, skip: int = 0, limit: int = 100) -> List[Post]:
        query = self.db.query(Post).filter(Post.date == target_date)
        return query.offset(skip).limit(limit).all()
