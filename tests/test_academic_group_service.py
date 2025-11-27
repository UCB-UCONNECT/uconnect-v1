"""
Testes unitários para AcademicGroupRepository e AcademicGroupService

Valida criação de grupos, atualização, adição e remoção de usuários.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.db.base import Base
from backend.app.models import User, UserRole, AccessStatus
from backend.app.repositories import AcademicGroupRepository, UserRepository
from backend.app.services import AcademicGroupService, UserService
from backend.app.core.security import get_password_hash


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def create_user(db: Session, registration: str = "2025101") -> User:
    repo = UserRepository(db)
    data = {
        "registration": registration,
        "name": "Usuário Grupo",
        "email": f"{registration}@example.com",
        "passwordHash": get_password_hash("senha123"),
        "role": UserRole.student,
        "accessStatus": AccessStatus.active,
    }
    return repo.create(data)


def test_create_group_and_list(test_db: Session):
    service = AcademicGroupService(test_db)
    group = service.create_group({"course": "Engenharia", "classGroup": "ENG-101", "subject": "Cálculo"})

    assert group.id is not None
    assert group.classGroup == "ENG-101"

    groups = service.list_groups()
    assert any(g.classGroup == "ENG-101" for g in groups)


def test_add_and_remove_user_from_group(test_db: Session):
    user = create_user(test_db, "2025102")
    service = AcademicGroupService(test_db)

    group = service.create_group({"course": "Direito", "classGroup": "DIR-201", "subject": "Constitucional"})

    # adicionar usuário
    updated = service.add_user_to_group(group.id, user.id)
    assert updated is not None
    assert any(u.id == user.id for u in updated.users)

    # remover usuário
    removed = service.remove_user_from_group(group.id, user.id)
    assert removed is True

    # tentar remover novamente deve retornar False
    removed_again = service.remove_user_from_group(group.id, user.id)
    assert removed_again is False
