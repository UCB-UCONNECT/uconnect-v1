"""
Testes Unitários para UserRepository e UserService

Valida a camada de repositório e serviço com mocks de BD.
Estes testes rodam rápido pois não acessam BD real.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.db.base import Base
from backend.app.models import User, UserRole, AccessStatus
from backend.app.repositories import UserRepository
from backend.app.services import UserService
from backend.app.core.security import get_password_hash


# Fixture: Banco de dados em memória para testes
@pytest.fixture
def test_db():
    """Cria um banco de dados SQLite em memória para testes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db
    
    db.close()


class TestUserRepository:
    """Testes para UserRepository."""
    
    def test_create_user(self, test_db: Session):
        """Testa criação de usuário."""
        repo = UserRepository(test_db)
        
        user_data = {
            "registration": "2023001",
            "name": "João Silva",
            "email": "joao@example.com",
            "passwordHash": get_password_hash("senha123"),
            "role": UserRole.student,
            "accessStatus": AccessStatus.active
        }
        
        user = repo.create(user_data)
        
        assert user.id is not None
        assert user.registration == "2023001"
        assert user.name == "João Silva"
        assert user.email == "joao@example.com"
    
    def test_get_user_by_id(self, test_db: Session):
        """Testa busca de usuário por ID."""
        repo = UserRepository(test_db)
        
        user_data = {
            "registration": "2023002",
            "name": "Maria Santos",
            "email": "maria@example.com",
            "passwordHash": get_password_hash("senha123"),
            "role": UserRole.teacher,
            "accessStatus": AccessStatus.active
        }
        
        user = repo.create(user_data)
        found = repo.get_by_id(user.id)
        
        assert found is not None
        assert found.id == user.id
        assert found.name == "Maria Santos"
    
    def test_get_by_registration(self, test_db: Session):
        """Testa busca por matrícula."""
        repo = UserRepository(test_db)
        
        user_data = {
            "registration": "2023003",
            "name": "Pedro Costa",
            "email": "pedro@example.com",
            "passwordHash": get_password_hash("senha123"),
            "role": UserRole.coordinator,
            "accessStatus": AccessStatus.active
        }
        
        repo.create(user_data)
        found = repo.get_by_registration("2023003")
        
        assert found is not None
        assert found.name == "Pedro Costa"
    
    def test_get_by_email(self, test_db: Session):
        """Testa busca por email."""
        repo = UserRepository(test_db)
        
        user_data = {
            "registration": "2023004",
            "name": "Ana Ferreira",
            "email": "ana@example.com",
            "passwordHash": get_password_hash("senha123"),
            "role": UserRole.student,
            "accessStatus": AccessStatus.active
        }
        
        repo.create(user_data)
        found = repo.get_by_email("ana@example.com")
        
        assert found is not None
        assert found.name == "Ana Ferreira"
    
    def test_list_by_role(self, test_db: Session):
        """Testa listagem de usuários por papel."""
        repo = UserRepository(test_db)
        
        # Criar usuários com diferentes papéis
        for i, role in enumerate([UserRole.student, UserRole.student, UserRole.teacher]):
            repo.create({
                "registration": f"2023{100+i}",
                "name": f"Usuário {i}",
                "email": f"user{i}@example.com",
                "passwordHash": get_password_hash("senha123"),
                "role": role,
                "accessStatus": AccessStatus.active
            })
        
        students = repo.list_by_role(UserRole.student)
        teachers = repo.list_by_role(UserRole.teacher)
        
        assert len(students) == 2
        assert len(teachers) == 1
    
    def test_registration_exists(self, test_db: Session):
        """Testa verificação de existência de matrícula."""
        repo = UserRepository(test_db)
        
        repo.create({
            "registration": "2023200",
            "name": "Teste",
            "email": "teste@example.com",
            "passwordHash": get_password_hash("senha123"),
            "role": UserRole.student,
            "accessStatus": AccessStatus.active
        })
        
        assert repo.registration_exists("2023200") is True
        assert repo.registration_exists("9999999") is False
    
    def test_update_user(self, test_db: Session):
        """Testa atualização de usuário."""
        repo = UserRepository(test_db)
        
        user = repo.create({
            "registration": "2023300",
            "name": "Original",
            "email": "original@example.com",
            "passwordHash": get_password_hash("senha123"),
            "role": UserRole.student,
            "accessStatus": AccessStatus.active
        })
        
        updated = repo.update(user.id, {"name": "Modificado", "email": "novo@example.com"})
        
        assert updated is not None
        assert updated.name == "Modificado"
        assert updated.email == "novo@example.com"
    
    def test_delete_user(self, test_db: Session):
        """Testa deleção de usuário."""
        repo = UserRepository(test_db)
        
        user = repo.create({
            "registration": "2023400",
            "name": "Para Deletar",
            "email": "delete@example.com",
            "passwordHash": get_password_hash("senha123"),
            "role": UserRole.student,
            "accessStatus": AccessStatus.active
        })
        
        deleted = repo.delete(user.id)
        found = repo.get_by_id(user.id)
        
        assert deleted is True
        assert found is None


class TestUserService:
    """Testes para UserService."""
    
    def test_create_user_success(self, test_db: Session):
        """Testa criação bem-sucedida de usuário."""
        service = UserService(test_db)
        
        user = service.create_user(
            registration="2023500",
            name="Novo Usuário",
            email="novo@example.com",
            password="senha123",
            role=UserRole.student
        )
        
        assert user.id is not None
        assert user.registration == "2023500"
        assert user.name == "Novo Usuário"
    
    def test_create_user_duplicate_registration(self, test_db: Session):
        """Testa falha ao criar usuário com matrícula duplicada."""
        from fastapi import HTTPException
        
        service = UserService(test_db)
        
        # Criar primeiro usuário
        service.create_user(
            registration="2023600",
            name="Primeiro",
            email="primeiro@example.com",
            password="senha123",
            role=UserRole.student
        )
        
        # Tentar criar outro com mesma matrícula deve falhar
        with pytest.raises(HTTPException) as exc:
            service.create_user(
                registration="2023600",
                name="Segundo",
                email="segundo@example.com",
                password="senha123",
                role=UserRole.student
            )
        
        assert exc.value.status_code == 400
    
    def test_authenticate_user_success(self, test_db: Session):
        """Testa autenticação bem-sucedida."""
        service = UserService(test_db)
        
        # Criar usuário
        service.create_user(
            registration="2023700",
            name="Auth Test",
            email="auth@example.com",
            password="senha123",
            role=UserRole.student
        )
        
        # Autenticar com credenciais corretas
        user = service.authenticate_user("2023700", "senha123")
        
        assert user is not None
        assert user.registration == "2023700"
    
    def test_authenticate_user_wrong_password(self, test_db: Session):
        """Testa falha de autenticação com senha incorreta."""
        service = UserService(test_db)
        
        # Criar usuário
        service.create_user(
            registration="2023800",
            name="Auth Test",
            email="auth2@example.com",
            password="senha123",
            role=UserRole.student
        )
        
        # Tentar autenticar com senha incorreta
        user = service.authenticate_user("2023800", "senhaerrada")
        
        assert user is None
    
    def test_list_users(self, test_db: Session):
        """Testa listagem de usuários."""
        service = UserService(test_db)
        
        # Criar vários usuários
        for i in range(3):
            service.create_user(
                registration=f"2023{900+i}",
                name=f"Usuário {i}",
                email=f"user{900+i}@example.com",
                password="senha123",
                role=UserRole.student
            )
        
        users = service.list_users(skip=0, limit=10)
        
        assert len(users) >= 3
    
    def test_count_users(self, test_db: Session):
        """Testa contagem de usuários."""
        service = UserService(test_db)
        
        initial_count = service.count_users()
        
        service.create_user(
            registration="2024000",
            name="Contagem",
            email="contagem@example.com",
            password="senha123",
            role=UserRole.student
        )
        
        final_count = service.count_users()
        
        assert final_count == initial_count + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
