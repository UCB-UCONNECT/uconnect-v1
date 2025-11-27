from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories import PostRepository
from ..models import Post


class PostService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PostRepository(db)

    def create_post(self, payload: Dict[str, Any]) -> Post:
        if not payload.get("title") or not payload.get("content") or not payload.get("authorId"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados incompletos para post")

        post = self.repo.create(payload)
        return post

    def get_post(self, post_id: int) -> Optional[Post]:
        return self.repo.get_by_id(post_id)

    def list_posts(self, skip: int = 0, limit: int = 20) -> List[Post]:
        return self.repo.list(skip=skip, limit=limit, order_by="date", reverse=True)

    def update_post(self, post_id: int, data: Dict[str, Any]) -> Optional[Post]:
        return self.repo.update(post_id, data)

    def delete_post(self, post_id: int) -> bool:
        return self.repo.delete(post_id)
