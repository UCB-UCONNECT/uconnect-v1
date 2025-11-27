from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories import AcademicGroupRepository
from ..models import AcademicGroup


class AcademicGroupService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AcademicGroupRepository(db)

    def create_group(self, payload: Dict[str, Any]) -> AcademicGroup:
        if not payload.get("classGroup") or not payload.get("course"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados incompletos para grupo académico")

        group = self.repo.create(payload)
        return group

    def get_group(self, group_id: int) -> Optional[AcademicGroup]:
        return self.repo.get_by_id(group_id)

    def list_groups(self, skip: int = 0, limit: int = 50) -> List[AcademicGroup]:
        return self.repo.list(skip=skip, limit=limit)

    def update_group(self, group_id: int, data: Dict[str, Any]) -> Optional[AcademicGroup]:
        return self.repo.update(group_id, data)

    def delete_group(self, group_id: int) -> bool:
        return self.repo.delete(group_id)

    def add_user_to_group(self, group_id: int, user_id: int) -> Optional[AcademicGroup]:
        group = self.repo.get_by_id(group_id)
        if not group:
            return None

        from ..models import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        if user in group.users:
            return group

        group.users.append(user)
        self.db.commit()
        self.db.refresh(group)
        return group

    def remove_user_from_group(self, group_id: int, user_id: int) -> bool:
        group = self.repo.get_by_id(group_id)
        if not group:
            return False

        from ..models import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        if user not in group.users:
            return False

        group.users.remove(user)
        self.db.commit()
        return True
