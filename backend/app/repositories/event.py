"""
EventRepository - Repositório Específico para Entidade Event

Estende GenericRepository com operações específicas para eventos:
- Buscar eventos por data
- Buscar eventos por criador
- Buscar eventos por grupo acadêmico
- Listar eventos futuros/passados
"""

from typing import Optional, List
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from .base import GenericRepository
from ..models import Event


class EventRepository(GenericRepository[Event]):
    """
    Repositório para operações com eventos.
    
    Exemplo de uso:
        repo = EventRepository(db)
        today_events = repo.get_events_by_date(date.today())
        creator_events = repo.get_by_creator(creator_id=1)
    """

    def __init__(self, db: Session):
        """Inicializa com modelo Event."""
        super().__init__(db, Event)

    def get_by_creator(self, creator_id: int, skip: int = 0, limit: int = 100) -> List[Event]:
        """
        Busca eventos criados por um usuário específico.
        
        Args:
            creator_id: ID do criador
            skip: Offset para paginação
            limit: Limite de registros
            
        Returns:
            Lista de eventos criados pelo usuário
        """
        return self.find_all_by_filter(skip=skip, limit=limit, creatorId=creator_id)

    def get_events_by_date(self, target_date: date, skip: int = 0, limit: int = 100) -> List[Event]:
        """
        Busca eventos para uma data específica.
        
        Args:
            target_date: Data dos eventos a buscar
            skip: Offset para paginação
            limit: Limite de registros
            
        Returns:
            Lista de eventos na data especificada
        """
        query = self.db.query(Event).filter(Event.eventDate == target_date)
        return query.offset(skip).limit(limit).all()

    def get_events_by_academic_group(self, group_id: str, skip: int = 0, limit: int = 100) -> List[Event]:
        """
        Busca eventos de um grupo acadêmico específico.
        
        Args:
            group_id: ID do grupo acadêmico
            skip: Offset para paginação
            limit: Limite de registros
            
        Returns:
            Lista de eventos do grupo
        """
        return self.find_all_by_filter(skip=skip, limit=limit, academicGroupId=group_id)

    def get_upcoming_events(self, days_ahead: int = 7, from_date: Optional[date] = None, skip: int = 0, limit: int = 100) -> List[Event]:
        """
        Busca eventos futuros dentro de um intervalo a partir de `from_date` (por padrão hoje).

        Args:
            days_ahead: número de dias a partir de `from_date` para considerar próximos eventos
            from_date: data inicial (se None, usa hoje)
            skip: Offset para paginação
            limit: Limite de registros

        Returns:
            Lista de eventos futuros ordenados por data
        """
        if from_date is None:
            from_date = datetime.utcnow().date()

        until_date = from_date + timedelta(days=days_ahead)

        query = self.db.query(Event).filter(Event.eventDate >= from_date, Event.eventDate <= until_date).order_by(Event.eventDate.asc())
        return query.offset(skip).limit(limit).all()

    def get_past_events(self, until_date: date, skip: int = 0, limit: int = 100) -> List[Event]:
        """
        Busca eventos passados até uma data.
        
        Args:
            until_date: Data final (eventos <= esta data)
            skip: Offset para paginação
            limit: Limite de registros
            
        Returns:
            Lista de eventos passados ordenados por data (decrescente)
        """
        query = self.db.query(Event).filter(Event.eventDate <= until_date).order_by(Event.eventDate.desc())
        return query.offset(skip).limit(limit).all()

    def count_by_creator(self, creator_id: int) -> int:
        """
        Conta eventos criados por um usuário.
        
        Args:
            creator_id: ID do criador
            
        Returns:
            Número de eventos criados
        """
        return self.count(creatorId=creator_id)

    def count_by_date(self, target_date: date) -> int:
        """
        Conta eventos em uma data específica.
        
        Args:
            target_date: Data para contar eventos
            
        Returns:
            Número de eventos na data
        """
        query = self.db.query(Event).filter(Event.eventDate == target_date)
        return query.count()
