"""
Serviço de Eventos (Event Service)

Camada de lógica de negócio para operações relacionadas a eventos.
Orquestra o repositório de eventos com validações de negócio.

Padrão:
    - Validações de entrada
    - Verificações de autorização
    - Chamadas ao repositório
    - Tratamento de erros de negócio
    - Retorno de dados processados

Responsabilidades:
    - Criação de eventos com validações
    - Consultas filtradas por diferentes critérios
    - Atualização com verificação de permissões
    - Deleção com cascata apropriada
    - Agregações (contagem, estatísticas)
"""

from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models import Event, User, UserRole, AcademicGroup
from backend.app.repositories.event import EventRepository
from backend.app.schemas import EventCreate, EventUpdate


class EventService:
    """
    Serviço de eventos implementando lógica de negócio.
    
    Responsabilidades:
        - Validar dados de entrada
        - Verificar permissões (apenas criador pode editar/deletar)
        - Garantir integridade de dados
        - Retornar dados processados
    
    Exemplo de uso:
        service = EventService(db)
        event = service.create_event(
            title="Reunião",
            description="...",
            creator_id=1,
            scheduled_date=datetime.now()
        )
    """
    
    def __init__(self, db: Session):
        """Inicializa o serviço com sessão do BD."""
        self.db = db
        self.repo = EventRepository(db)
    
    # ========== OPERAÇÕES CRUD ==========
    
    def create_event(
        self,
        title: str,
        description: str,
        creator_id: int,
        scheduled_date: datetime,
        academic_group_id: Optional[int] = None,
        visibility: str = "public",
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
    ) -> Event:
        """
        Cria novo evento com validações.
        
        Validações:
            - Título não vazio
            - Data no futuro
            - Creator existe
            - Academic group existe (se fornecido)
        
        Args:
            title: Título do evento
            description: Descrição
            creator_id: ID do criador
            scheduled_date: Data do evento
            academic_group_id: ID do grupo académico (opcional)
            visibility: "public" ou "private"
        
        Returns:
            Event criado
        
        Raises:
            HTTPException(400): Se título vazio
            HTTPException(400): Se data não está no futuro
            HTTPException(404): Se criador não existe
            HTTPException(404): Se grupo académico não existe
        
        Exemplo:
            event = service.create_event(
                title="Seminário",
                description="Palestra sobre IA",
                creator_id=1,
                scheduled_date=datetime.now() + timedelta(days=7),
                academic_group_id=2
            )
        """
        # Validação: título não vazio
        if not title or not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Título do evento não pode estar vazio"
            )
        
        # Validação: data no futuro (normaliza para date)
        now_date = datetime.now().date()
        sched_date = scheduled_date.date() if isinstance(scheduled_date, datetime) else scheduled_date
        if sched_date <= now_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data do evento deve estar no futuro"
            )
        
        # Validação: criador existe
        creator = self.db.query(User).filter(User.id == creator_id).first()
        if not creator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário criador não encontrado"
            )
        
        # Validação: grupo académico existe (se fornecido)
        if academic_group_id:
            import logging
            logger = logging.getLogger("uvicorn.error")
            logger.info(f"[EVENT] Validando academic_group_id: {academic_group_id} (tipo: {type(academic_group_id)})")
            
            # Converter para int se for string numérica, caso contrário ignorar
            try:
                group_id_int = int(academic_group_id) if isinstance(academic_group_id, str) else academic_group_id
            except (ValueError, TypeError):
                logger.warning(f"[EVENT] academic_group_id inválido (não numérico): {academic_group_id} - ignorando e criando sem grupo")
                academic_group_id = None
            else:
                group = self.db.query(AcademicGroup).filter(
                    AcademicGroup.id == group_id_int
                ).first()
                logger.info(f"[EVENT] Grupo encontrado: {group}")
                if not group:
                    logger.warning(f"[EVENT] Grupo académico não encontrado: {group_id_int} - criando sem grupo")
                    academic_group_id = None
                else:
                    academic_group_id = group_id_int
                    logger.info(f"[EVENT] Criando evento com grupo acadêmico: {group_id_int}")
        
        # Criação
        event_data = {
            "title": title.strip(),
            "description": description.strip() if description else "",
            "timestamp": datetime.now(),
            "eventDate": sched_date,
            "startTime": start_time,
            "endTime": end_time,
            "academicGroupId": academic_group_id,
            "creatorId": creator_id
        }
        
        return self.repo.create(event_data)
    
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """
        Obtém evento por ID.
        
        Args:
            event_id: ID do evento
        
        Returns:
            Event ou None se não encontrado
        
        Exemplo:
            event = service.get_event_by_id(5)
        """
        return self.repo.get_by_id(event_id)
    
    def list_events(
        self,
        skip: int = 0,
        limit: int = 10,
        order_by: str = "eventDate",
        reverse: bool = False
    ) -> List[Event]:
        """
        Lista todos os eventos com paginação.
        
        Args:
            skip: Quantidade de eventos a pular
            limit: Quantidade máxima de eventos
            order_by: Campo para ordenação (padrão: `eventDate` - data agendada)
            reverse: Se verdadeiro, ordena em reverso
        
        Returns:
            Lista de eventos
        
        Exemplo:
            events = service.list_events(skip=0, limit=20)
        """
        return self.repo.list(skip=skip, limit=limit, order_by=order_by, reverse=reverse)
    
    def list_events_by_creator(
        self,
        creator_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Event]:
        """
        Lista eventos criados por um usuário.
        
        Args:
            creator_id: ID do criador
            skip: Paginação
            limit: Limite de resultados
        
        Returns:
            Lista de eventos do criador
        
        Exemplo:
            my_events = service.list_events_by_creator(creator_id=1)
        """
        return self.repo.get_by_creator(creator_id, skip=skip, limit=limit)
    
    def get_upcoming_events(
        self,
        days_ahead: int = 7,
        skip: int = 0,
        limit: int = 10
    ) -> List[Event]:
        """
        Lista eventos próximos (nos próximos N dias).
        
        Args:
            days_ahead: Número de dias futuros (padrão: 7)
            skip: Paginação
            limit: Limite de resultados
        
        Returns:
            Lista de eventos próximos
        
        Exemplo:
            upcoming = service.get_upcoming_events(days_ahead=14)
        """
        return self.repo.get_upcoming_events(days_ahead=days_ahead, skip=skip, limit=limit)
    
    def get_past_events(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[Event]:
        """
        Lista eventos já ocorridos.
        
        Args:
            skip: Paginação
            limit: Limite de resultados
        
        Returns:
            Lista de eventos passados
        
        Exemplo:
            past = service.get_past_events()
        """
        return self.repo.get_past_events(skip=skip, limit=limit)
    
    def update_event(
        self,
        event_id: int,
        current_user: User,
        update_data: Dict[str, Any]
    ) -> Optional[Event]:
        """
        Atualiza evento com verificação de permissão.
        
        Validações:
            - Event existe
            - Current user é o criador
            - Dados são válidos
        
        Args:
            event_id: ID do evento
            current_user: Usuário realizando atualização
            update_data: Dados a atualizar
        
        Returns:
            Event atualizado ou None se não encontrado
        
        Raises:
            HTTPException(404): Se evento não existe
            HTTPException(403): Se user não é criador
        
        Exemplo:
            updated = service.update_event(
                event_id=5,
                current_user=user,
                update_data={"title": "Novo Título"}
            )
        """
        # Validar que evento existe
        event = self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Validar autorização (criador ou admin)
        import logging
        logger = logging.getLogger("uvicorn.error")
        logger.info(f"[EVENT] Validando permissão de edição: event.creatorId={event.creatorId}, current_user.id={current_user.id}, role={current_user.role.value}")
        if event.creatorId != current_user.id and current_user.role.value != 'admin':
            logger.warning(f"[EVENT] Permissão negada para edição: usuário {current_user.id} não é criador nem admin")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o criador do evento ou um administrador pode editá-lo"
            )
        
        # Aplicar atualizações
        return self.repo.update(event_id, update_data)
    
    def delete_event(self, event_id: int, current_user: User) -> bool:
        """
        Deleta evento com verificação de permissão.
        
        Validações:
            - Event existe
            - Current user é o criador OU é admin
        
        Args:
            event_id: ID do evento
            current_user: Usuário realizando deleção
        
        Returns:
            True se deletado, False se não encontrado
        
        Raises:
            HTTPException(403): Se user não é criador e não é admin
        
        Exemplo:
            deleted = service.delete_event(event_id=5, current_user=user)
        """
        # Validar que evento existe
        event = self.repo.get_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento não encontrado"
            )
        
        # Validar autorização (criador OU admin)
        import logging
        logger = logging.getLogger("uvicorn.error")
        is_creator = event.creatorId == current_user.id
        is_admin = current_user.role.value == 'admin'
        logger.info(f"[EVENT] Validando permissão de deleção: is_creator={is_creator}, is_admin={is_admin}, role={current_user.role.value}")
        
        if not is_creator and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o criador ou administrador pode deletar este evento"
            )
        
        return self.repo.delete(event_id)
    
    # ========== OPERAÇÕES DE FILTRO ==========
    
    def list_events_by_academic_group(
        self,
        academic_group_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Event]:
        """
        Lista eventos de um grupo académico específico.
        
        Args:
            academic_group_id: ID do grupo
            skip: Paginação
            limit: Limite de resultados
        
        Returns:
            Lista de eventos do grupo
        
        Exemplo:
            group_events = service.list_events_by_academic_group(academic_group_id=2)
        """
        return self.repo.get_events_by_academic_group(
            academic_group_id, skip=skip, limit=limit
        )
    
    def get_events_by_date(
        self,
        target_date: datetime,
        skip: int = 0,
        limit: int = 10
    ) -> List[Event]:
        """
        Lista eventos em uma data específica.
        
        Args:
            target_date: Data alvo
            skip: Paginação
            limit: Limite de resultados
        
        Returns:
            Lista de eventos da data
        
        Exemplo:
            today_events = service.get_events_by_date(datetime.now().date())
        """
        return self.repo.get_events_by_date(target_date, skip=skip, limit=limit)
    
    # ========== OPERAÇÕES DE CONTAGEM ==========
    
    def count_events(self) -> int:
        """
        Conta total de eventos.
        
        Returns:
            Número total de eventos
        
        Exemplo:
            total = service.count_events()
        """
        return self.repo.count()
    
    def count_events_by_creator(self, creator_id: int) -> int:
        """
        Conta eventos de um criador.
        
        Args:
            creator_id: ID do criador
        
        Returns:
            Número de eventos do criador
        
        Exemplo:
            my_count = service.count_events_by_creator(creator_id=1)
        """
        return self.repo.count_by_creator(creator_id)
    
    def count_upcoming_events(self, days_ahead: int = 7) -> int:
        """
        Conta eventos próximos.
        
        Args:
            days_ahead: Número de dias (padrão: 7)
        
        Returns:
            Número de eventos próximos
        
        Exemplo:
            upcoming_count = service.count_upcoming_events(days_ahead=30)
        """
        return self.repo.count_upcoming_events(days_ahead=days_ahead)
    
    def count_events_by_date(self, target_date: datetime) -> int:
        """
        Conta eventos em uma data específica.
        
        Args:
            target_date: Data alvo
        
        Returns:
            Número de eventos da data
        
        Exemplo:
            today_count = service.count_events_by_date(datetime.now().date())
        """
        return self.repo.count_by_date(target_date)
    
    # ========== OPERAÇÕES DE VERIFICAÇÃO ==========
    
    def event_exists(self, event_id: int) -> bool:
        """
        Verifica se evento existe.
        
        Args:
            event_id: ID do evento
        
        Returns:
            True se existe, False caso contrário
        
        Exemplo:
            exists = service.event_exists(event_id=5)
        """
        return self.repo.exists(id=event_id)
    
    def event_belongs_to_user(self, event_id: int, user_id: int) -> bool:
        """
        Verifica se evento pertence a um usuário (ele é criador).
        
        Args:
            event_id: ID do evento
            user_id: ID do usuário
        
        Returns:
            True se user é criador, False caso contrário
        
        Exemplo:
            is_mine = service.event_belongs_to_user(event_id=5, user_id=1)
        """
        event = self.repo.get_by_id(event_id)
        return event is not None and event.creatorId == user_id
