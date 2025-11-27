from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories import AnnouncementRepository
from ..models import Announcement


class AnnouncementService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnnouncementRepository(db)

    def create_announcement(self, payload: Dict[str, Any]) -> Announcement:
        if not payload.get("title") or not payload.get("content") or not payload.get("authorId"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados incompletos para comunicado")

        ann = self.repo.create(payload)
        return ann

    def get_announcement(self, announcement_id: int) -> Optional[Announcement]:
        return self.repo.get_by_id(announcement_id)

    def list_announcements(self, skip: int = 0, limit: int = 50) -> List[Announcement]:
        return self.repo.list(skip=skip, limit=limit, order_by="date", reverse=True)

    def update_announcement(self, announcement_id: int, data: Dict[str, Any]) -> Optional[Announcement]:
        return self.repo.update(announcement_id, data)

    def delete_announcement(self, announcement_id: int) -> bool:
        return self.repo.delete(announcement_id)
