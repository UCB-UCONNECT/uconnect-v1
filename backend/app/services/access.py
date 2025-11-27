from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories import AccessRepository, UserRepository
from ..models import AccessManager


class AccessService:
    """Serviço de negócio para gerenciar permissões (AccessManager)."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AccessRepository(db)
        self.user_repo = UserRepository(db)

    def create_access(self, access_data: Dict[str, Any]) -> AccessManager:
        user = self.user_repo.get_by_id(access_data.get("userId"))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return self.repo.create(access_data)

    def list_user_permissions(self, user_id: int) -> List[AccessManager]:
        return self.repo.list_by_user(user_id)

    def list_all_permissions(self) -> List[AccessManager]:
        return self.repo.list()

    def update_permission(self, access_id: int, update_data: Dict[str, Any]) -> Optional[AccessManager]:
        access = self.repo.get_by_id(access_id)
        if not access:
            return None
        return self.repo.update(access_id, update_data)

    def delete_permission(self, access_id: int) -> bool:
        return self.repo.delete(access_id)

    def check_permission(self, user_id: int, permission: str) -> bool:
        return self.repo.find_permission(user_id, permission) is not None
