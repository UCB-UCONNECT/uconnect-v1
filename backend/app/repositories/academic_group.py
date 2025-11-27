from typing import List, Optional
from sqlalchemy.orm import Session
from .base import GenericRepository
from ..models import AcademicGroup


class AcademicGroupRepository(GenericRepository[AcademicGroup]):
    """Repositório para AcademicGroup com consultas específicas."""

    def __init__(self, db: Session):
        super().__init__(db, AcademicGroup)

    def get_by_coordinator(self, coordinator_id: int, skip: int = 0, limit: int = 100) -> List[AcademicGroup]:
        if hasattr(AcademicGroup, 'coordinatorId'):
            return self.find_all_by_filter(skip=skip, limit=limit, coordinatorId=coordinator_id)
        return []

    def get_by_class_group(self, class_group: str) -> Optional[AcademicGroup]:
        return self.find_by_filter(classGroup=class_group)
