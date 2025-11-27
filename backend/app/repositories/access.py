from typing import List, Optional
from sqlalchemy.orm import Session

from .base import GenericRepository
from ..models import AccessManager


class AccessRepository(GenericRepository[AccessManager]):
    """
    Repositório específico para AccessManager.
    """

    def __init__(self, db: Session):
        super().__init__(db, AccessManager)

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AccessManager]:
        return self.find_all_by_filter(skip=skip, limit=limit, userId=user_id)

    def find_permission(self, user_id: int, permission: str) -> Optional[AccessManager]:
        return self.find_by_filter(userId=user_id, permission=permission)
