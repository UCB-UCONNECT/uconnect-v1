"""
Testes unitários para PostRepository e PostService

Valida operações básicas: criação, listagem, obtenção, atualização e deleção.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.db.base import Base
from backend.app.models import User, UserRole, AccessStatus
from backend.app.repositories import PostRepository, UserRepository
from backend.app.services import PostService, UserService
from backend.app.core.security import get_password_hash


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def create_user_for_tests(db: Session, registration: str = "2025001") -> User:
    user_repo = UserRepository(db)
    user_data = {
        "registration": registration,
        "name": "Autor Test",
        "email": f"{registration}@example.com",
        "passwordHash": get_password_hash("senha123"),
        "role": UserRole.student,
        "accessStatus": AccessStatus.active,
    }
    return user_repo.create(user_data)


def test_create_post_success(test_db: Session):
    user = create_user_for_tests(test_db)
    service = PostService(test_db)

    payload = {"title": "Olá", "content": "Conteúdo do post", "authorId": user.id}
    post = service.create_post(payload)

    assert post.id is not None
    assert post.title == "Olá"
    assert post.authorId == user.id


def test_create_post_missing_fields(test_db: Session):
    service = PostService(test_db)
    with pytest.raises(Exception):
        service.create_post({"title": "Só título"})


def test_list_and_get_post(test_db: Session):
    user = create_user_for_tests(test_db, "2025002")
    service = PostService(test_db)

    p1 = service.create_post({"title": "P1", "content": "C1", "authorId": user.id})
    p2 = service.create_post({"title": "P2", "content": "C2", "authorId": user.id})

    posts = service.list_posts(skip=0, limit=10)
    assert len(posts) >= 2

    found = service.get_post(p1.id)
    assert found is not None
    assert found.title == "P1"


def test_update_and_delete_post(test_db: Session):
    user = create_user_for_tests(test_db, "2025003")
    service = PostService(test_db)

    post = service.create_post({"title": "Antes", "content": "X", "authorId": user.id})
    updated = service.update_post(post.id, {"title": "Depois"})

    assert updated is not None
    assert updated.title == "Depois"

    deleted = service.delete_post(post.id)
    assert deleted is True
    assert service.get_post(post.id) is None
