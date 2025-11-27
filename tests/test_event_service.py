"""
Testes para EventRepository e EventService

Este módulo contém testes unitários que validam:
- Operações CRUD do EventRepository
- Lógica de negócio do EventService
- Validações de autorização
- Casos extremos e erros

Usa SQLite em memória para testes rápidos e isolados.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException, status

from backend.app.db.base import Base
from backend.app.models import Event, User, UserRole, AccessStatus, AcademicGroup
from backend.app.repositories.event import EventRepository
from backend.app.services.event import EventService
from backend.app.core.security import get_password_hash


# ========== FIXTURES ==========

@pytest.fixture(scope="function")
def test_db():
    """Cria BD em memória limpa para cada teste."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_user(test_db: Session) -> User:
    """Cria usuário de exemplo para testes."""
    user = User(
        registration="2023001",
        name="João Silva",
        email="joao@example.com",
        hashed_password=get_password_hash("senha123"),
        role=UserRole.STUDENT,
        access_status=AccessStatus.ACTIVE,
        created_at=datetime.now()
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_user(test_db: Session) -> User:
    """Cria usuário admin para testes."""
    admin = User(
        registration="admin001",
        name="Admin User",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        access_status=AccessStatus.ACTIVE,
        created_at=datetime.now()
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def sample_academic_group(test_db: Session) -> AcademicGroup:
    """Cria grupo académico de exemplo."""
    group = AcademicGroup(
        name="Engenharia Informática",
        description="Curso de Engenharia Informática",
        coordinator_id=1,
        created_at=datetime.now()
    )
    test_db.add(group)
    test_db.commit()
    test_db.refresh(group)
    return group


# ========== TESTES DO REPOSITÓRIO ==========

class TestEventRepository:
    """Testes para EventRepository."""
    
    def test_create_event(self, test_db: Session, sample_user: User):
        """Testa criação de evento."""
        repo = EventRepository(test_db)
        
        event_data = {
            "title": "Seminário de IA",
            "description": "Palestra sobre inteligência artificial",
            "creator_id": sample_user.id,
            "scheduled_date": datetime.now() + timedelta(days=7),
            "visibility": "public",
            "created_at": datetime.now()
        }
        
        event = repo.create(event_data)
        
        assert event is not None
        assert event.id is not None
        assert event.title == "Seminário de IA"
        assert event.creator_id == sample_user.id
    
    def test_get_event_by_id(self, test_db: Session, sample_user: User):
        """Testa busca de evento por ID."""
        repo = EventRepository(test_db)
        
        event = repo.create({
            "title": "Reunião",
            "description": "Reunião de equipe",
            "creator_id": sample_user.id,
            "scheduled_date": datetime.now() + timedelta(days=1),
            "created_at": datetime.now()
        })
        
        found = repo.get_by_id(event.id)
        
        assert found is not None
        assert found.id == event.id
        assert found.title == "Reunião"
    
    def test_get_event_by_id_not_found(self, test_db: Session):
        """Testa busca de evento que não existe."""
        repo = EventRepository(test_db)
        found = repo.get_by_id(999)
        assert found is None
    
    def test_list_events(self, test_db: Session, sample_user: User):
        """Testa listagem de eventos."""
        repo = EventRepository(test_db)
        
        # Criar 3 eventos
        for i in range(3):
            repo.create({
                "title": f"Evento {i+1}",
                "description": f"Descrição {i+1}",
                "creator_id": sample_user.id,
                "scheduled_date": datetime.now() + timedelta(days=i+1),
                "created_at": datetime.now()
            })
        
        events = repo.list(skip=0, limit=10)
        
        assert len(events) == 3
        assert events[0].title == "Evento 1"
    
    def test_get_event_by_creator(self, test_db: Session, sample_user: User):
        """Testa busca de eventos por criador."""
        repo = EventRepository(test_db)
        
        # Criar eventos do usuário
        for i in range(2):
            repo.create({
                "title": f"Evento do João {i+1}",
                "description": "...",
                "creator_id": sample_user.id,
                "scheduled_date": datetime.now() + timedelta(days=1),
                "created_at": datetime.now()
            })
        
        events = repo.get_by_creator(sample_user.id)
        
        assert len(events) == 2
        assert all(e.creator_id == sample_user.id for e in events)
    
    def test_get_upcoming_events(self, test_db: Session, sample_user: User):
        """Testa busca de eventos próximos."""
        repo = EventRepository(test_db)
        
        # Criar evento no futuro (3 dias)
        repo.create({
            "title": "Evento Futuro",
            "description": "...",
            "creator_id": sample_user.id,
            "scheduled_date": datetime.now() + timedelta(days=3),
            "created_at": datetime.now()
        })
        
        # Criar evento muito distante (30 dias)
        repo.create({
            "title": "Evento Distante",
            "description": "...",
            "creator_id": sample_user.id,
            "scheduled_date": datetime.now() + timedelta(days=30),
            "created_at": datetime.now()
        })
        
        # Buscar próximos 7 dias
        upcoming = repo.get_upcoming_events(days_ahead=7)
        
        assert len(upcoming) == 1
        assert upcoming[0].title == "Evento Futuro"
    
    def test_count_events(self, test_db: Session, sample_user: User):
        """Testa contagem de eventos."""
        repo = EventRepository(test_db)
        
        for i in range(5):
            repo.create({
                "title": f"Evento {i+1}",
                "description": "...",
                "creator_id": sample_user.id,
                "scheduled_date": datetime.now() + timedelta(days=1),
                "created_at": datetime.now()
            })
        
        count = repo.count()
        assert count == 5
    
    def test_count_events_by_creator(self, test_db: Session, sample_user: User):
        """Testa contagem de eventos por criador."""
        repo = EventRepository(test_db)
        
        for i in range(3):
            repo.create({
                "title": f"Evento {i+1}",
                "description": "...",
                "creator_id": sample_user.id,
                "scheduled_date": datetime.now() + timedelta(days=1),
                "created_at": datetime.now()
            })
        
        count = repo.count_by_creator(sample_user.id)
        assert count == 3
    
    def test_update_event(self, test_db: Session, sample_user: User):
        """Testa atualização de evento."""
        repo = EventRepository(test_db)
        
        event = repo.create({
            "title": "Título Original",
            "description": "Descrição Original",
            "creator_id": sample_user.id,
            "scheduled_date": datetime.now() + timedelta(days=1),
            "created_at": datetime.now()
        })
        
        updated = repo.update(event.id, {"title": "Título Atualizado"})
        
        assert updated is not None
        assert updated.title == "Título Atualizado"
        assert updated.description == "Descrição Original"  # Não mudou
    
    def test_delete_event(self, test_db: Session, sample_user: User):
        """Testa deleção de evento."""
        repo = EventRepository(test_db)
        
        event = repo.create({
            "title": "Evento para Deletar",
            "description": "...",
            "creator_id": sample_user.id,
            "scheduled_date": datetime.now() + timedelta(days=1),
            "created_at": datetime.now()
        })
        
        result = repo.delete(event.id)
        assert result is True
        
        # Verificar que foi deletado
        found = repo.get_by_id(event.id)
        assert found is None
    
    def test_event_exists(self, test_db: Session, sample_user: User):
        """Testa verificação de existência de evento."""
        repo = EventRepository(test_db)
        
        event = repo.create({
            "title": "Evento",
            "description": "...",
            "creator_id": sample_user.id,
            "scheduled_date": datetime.now() + timedelta(days=1),
            "created_at": datetime.now()
        })
        
        exists = repo.exists(id=event.id)
        assert exists is True
        
        not_exists = repo.exists(id=999)
        assert not_exists is False


# ========== TESTES DO SERVIÇO ==========

class TestEventService:
    """Testes para EventService."""
    
    def test_create_event_success(self, test_db: Session, sample_user: User):
        """Testa criação bem-sucedida de evento."""
        service = EventService(test_db)
        
        event = service.create_event(
            title="Seminário",
            description="Seminário de IA",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=7),
            visibility="public"
        )
        
        assert event is not None
        assert event.id is not None
        assert event.title == "Seminário"
        assert event.creator_id == sample_user.id
    
    def test_create_event_empty_title(self, test_db: Session, sample_user: User):
        """Testa criação de evento com título vazio."""
        service = EventService(test_db)
        
        with pytest.raises(HTTPException) as exc:
            service.create_event(
                title="",
                description="Descrição",
                creator_id=sample_user.id,
                scheduled_date=datetime.now() + timedelta(days=1)
            )
        
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "não pode estar vazio" in exc.value.detail
    
    def test_create_event_past_date(self, test_db: Session, sample_user: User):
        """Testa criação de evento com data no passado."""
        service = EventService(test_db)
        
        with pytest.raises(HTTPException) as exc:
            service.create_event(
                title="Seminário",
                description="...",
                creator_id=sample_user.id,
                scheduled_date=datetime.now() - timedelta(days=1)
            )
        
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "futuro" in exc.value.detail
    
    def test_create_event_creator_not_found(self, test_db: Session):
        """Testa criação de evento com criador inexistente."""
        service = EventService(test_db)
        
        with pytest.raises(HTTPException) as exc:
            service.create_event(
                title="Seminário",
                description="...",
                creator_id=999,
                scheduled_date=datetime.now() + timedelta(days=1)
            )
        
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND
        assert "criador" in exc.value.detail
    
    def test_get_event_by_id(self, test_db: Session, sample_user: User):
        """Testa busca de evento por ID."""
        service = EventService(test_db)
        
        created = service.create_event(
            title="Reunião",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        found = service.get_event_by_id(created.id)
        
        assert found is not None
        assert found.id == created.id
        assert found.title == "Reunião"
    
    def test_list_events(self, test_db: Session, sample_user: User):
        """Testa listagem de eventos."""
        service = EventService(test_db)
        
        for i in range(3):
            service.create_event(
                title=f"Evento {i+1}",
                description="...",
                creator_id=sample_user.id,
                scheduled_date=datetime.now() + timedelta(days=i+1)
            )
        
        events = service.list_events(skip=0, limit=10)
        
        assert len(events) == 3
    
    def test_update_event_success(self, test_db: Session, sample_user: User):
        """Testa atualização de evento."""
        service = EventService(test_db)
        
        event = service.create_event(
            title="Título Original",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        updated = service.update_event(
            event_id=event.id,
            current_user=sample_user,
            update_data={"title": "Título Novo"}
        )
        
        assert updated is not None
        assert updated.title == "Título Novo"
    
    def test_update_event_not_creator(self, test_db: Session, sample_user: User):
        """Testa atualização por usuário que não é criador."""
        service = EventService(test_db)
        
        # Criar evento com sample_user
        event = service.create_event(
            title="Evento Original",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        # Criar outro usuário
        other_user = User(
            registration="2023002",
            name="Outro Usuário",
            email="outro@example.com",
            hashed_password=get_password_hash("senha123"),
            role=UserRole.STUDENT,
            access_status=AccessStatus.ACTIVE,
            created_at=datetime.now()
        )
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)
        
        # Tentar atualizar com outro usuário
        with pytest.raises(HTTPException) as exc:
            service.update_event(
                event_id=event.id,
                current_user=other_user,
                update_data={"title": "Título Novo"}
            )
        
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_event_success(self, test_db: Session, sample_user: User):
        """Testa deleção de evento."""
        service = EventService(test_db)
        
        event = service.create_event(
            title="Evento para Deletar",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        result = service.delete_event(event_id=event.id, current_user=sample_user)
        assert result is True
        
        # Verificar que foi deletado
        found = service.get_event_by_id(event.id)
        assert found is None
    
    def test_delete_event_by_admin(self, test_db: Session, sample_user: User, admin_user: User):
        """Testa deleção de evento por admin."""
        service = EventService(test_db)
        
        event = service.create_event(
            title="Evento",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        # Admin pode deletar
        result = service.delete_event(event_id=event.id, current_user=admin_user)
        assert result is True
    
    def test_get_upcoming_events(self, test_db: Session, sample_user: User):
        """Testa busca de eventos próximos."""
        service = EventService(test_db)
        
        # Criar evento próximo
        service.create_event(
            title="Próximo",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=3)
        )
        
        # Criar evento distante
        service.create_event(
            title="Distante",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=30)
        )
        
        upcoming = service.get_upcoming_events(days_ahead=7)
        
        assert len(upcoming) == 1
        assert upcoming[0].title == "Próximo"
    
    def test_count_events(self, test_db: Session, sample_user: User):
        """Testa contagem de eventos."""
        service = EventService(test_db)
        
        for i in range(5):
            service.create_event(
                title=f"Evento {i+1}",
                description="...",
                creator_id=sample_user.id,
                scheduled_date=datetime.now() + timedelta(days=1)
            )
        
        count = service.count_events()
        assert count == 5
    
    def test_count_events_by_creator(self, test_db: Session, sample_user: User):
        """Testa contagem de eventos por criador."""
        service = EventService(test_db)
        
        for i in range(3):
            service.create_event(
                title=f"Evento {i+1}",
                description="...",
                creator_id=sample_user.id,
                scheduled_date=datetime.now() + timedelta(days=1)
            )
        
        count = service.count_events_by_creator(sample_user.id)
        assert count == 3
    
    def test_event_exists(self, test_db: Session, sample_user: User):
        """Testa verificação de existência."""
        service = EventService(test_db)
        
        event = service.create_event(
            title="Evento",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        assert service.event_exists(event.id) is True
        assert service.event_exists(999) is False
    
    def test_event_belongs_to_user(self, test_db: Session, sample_user: User):
        """Testa verificação de propriedade."""
        service = EventService(test_db)
        
        event = service.create_event(
            title="Evento",
            description="...",
            creator_id=sample_user.id,
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        assert service.event_belongs_to_user(event.id, sample_user.id) is True
        assert service.event_belongs_to_user(event.id, 999) is False
