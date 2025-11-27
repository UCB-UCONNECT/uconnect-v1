"""
UserRepository - Repositório Específico para Entidade User

Estende GenericRepository com operações específicas para usuários:
- Buscar por matrícula (registration)
- Buscar por email
- Listar usuários por role
- Listar usuários por status de acesso
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from .base import GenericRepository
from ..models import User, UserRole, AccessStatus


class UserRepository(GenericRepository[User]):
    """
    Repositório para operações com usuários.
    
    Exemplo de uso:
        repo = UserRepository(db)
        user = repo.get_by_registration("2023001")
        teachers = repo.list_by_role(UserRole.teacher)
    """

    def __init__(self, db: Session):
        """Inicializa com modelo User."""
        super().__init__(db, User)

    def get_by_registration(self, registration: str) -> Optional[User]:
        """
        Busca usuário pela matrícula.
        
        Args:
            registration: Matrícula do usuário
            
        Returns:
            Usuário encontrado ou None
        """
        return self.find_by_filter(registration=registration)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Busca usuário pelo email.
        
        Args:
            email: Email do usuário
            
        Returns:
            Usuário encontrado ou None
        """
        return self.find_by_filter(email=email)

    def list_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lista usuários por papel.
        
        Args:
            role: Papel do usuário (student, teacher, coordinator, admin)
            skip: Offset para paginação
            limit: Limite de registros
            
        Returns:
            Lista de usuários com o papel especificado
        """
        return self.find_all_by_filter(skip=skip, limit=limit, role=role)

    def list_by_access_status(self, status: AccessStatus, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lista usuários por status de acesso.
        
        Args:
            status: Status de acesso (active, inactive, suspended)
            skip: Offset para paginação
            limit: Limite de registros
            
        Returns:
            Lista de usuários com o status especificado
        """
        return self.find_all_by_filter(skip=skip, limit=limit, accessStatus=status)

    def registration_exists(self, registration: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica se uma matrícula já existe no sistema.
        
        Args:
            registration: Matrícula a verificar
            exclude_id: ID de usuário a excluir da busca (para updates)
            
        Returns:
            True se existe, False caso contrário
        """
        query = self.db.query(User).filter(User.registration == registration)
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica se um email já está cadastrado.
        
        Args:
            email: Email a verificar
            exclude_id: ID de usuário a excluir da busca (para updates)
            
        Returns:
            True se existe, False caso contrário
        """
        query = self.db.query(User).filter(User.email == email)
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None

    def count_by_role(self, role: UserRole) -> int:
        """
        Conta usuários com um papel específico.
        
        Args:
            role: Papel do usuário
            
        Returns:
            Número de usuários com o papel
        """
        return self.count(role=role)

    def count_by_status(self, status: AccessStatus) -> int:
        """
        Conta usuários com um status específico.
        
        Args:
            status: Status de acesso
            
        Returns:
            Número de usuários com o status
        """
        return self.count(accessStatus=status)
