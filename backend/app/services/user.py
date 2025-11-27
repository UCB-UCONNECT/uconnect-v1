"""
UserService - Serviço de Negócio para Usuários

Orquestra operações com usuários, implementando lógica de negócio:
- Validações de cadastro
- Gerenciamento de senhas
- Controle de acesso
- Validações de integridade

Exemplo de uso em um router:
    service = UserService(db)
    user = service.create_user(user_data)
    users = service.list_users(skip=0, limit=10)
"""

from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..repositories import UserRepository
from ..models import User, UserRole, AccessStatus
from ..core.security import get_password_hash, verify_password


class UserService:
    """
    Serviço de negócio para operações com usuários.
    
    Encapsula toda a lógica de negócio relacionada a usuários,
    separando da camada de HTTP (routers).
    """

    def __init__(self, db: Session):
        """
        Inicializa o serviço com sessão de BD.
        
        Args:
            db: Sessão SQLAlchemy ativa
        """
        self.db = db
        self.repo = UserRepository(db)

    def create_user(
        self,
        registration: str,
        name: str,
        email: str,
        password: str,
        role: UserRole
    ) -> User:
        """
        Cria um novo usuário com validações de negócio.
        
        Args:
            registration: Matrícula do usuário
            name: Nome completo
            email: Email
            password: Senha em texto plano (será hashada)
            role: Papel do usuário
            
        Returns:
            Usuário criado
            
        Raises:
            HTTPException: Se matrícula ou email já existem
        """
        # Validar matrícula única
        if self.repo.registration_exists(registration):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Matrícula já cadastrada no sistema"
            )
        
        # Validar email único
        if self.repo.email_exists(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado no sistema"
            )
        
        # Hash da senha
        hashed_password = get_password_hash(password)
        
        # Criar usuário
        user_data = {
            "registration": registration,
            "name": name,
            "email": email,
            "passwordHash": hashed_password,
            "role": role,
            "accessStatus": AccessStatus.active
        }
        
        return self.repo.create(user_data)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Busca um usuário pelo ID.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Usuário ou None se não encontrado
        """
        return self.repo.get_by_id(user_id)

    def get_user_by_registration(self, registration: str) -> Optional[User]:
        """
        Busca um usuário pela matrícula.
        
        Args:
            registration: Matrícula do usuário
            
        Returns:
            Usuário ou None se não encontrado
        """
        return self.repo.get_by_registration(registration)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Busca um usuário pelo email.
        
        Args:
            email: Email do usuário
            
        Returns:
            Usuário ou None se não encontrado
        """
        return self.repo.get_by_email(email)

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lista todos os usuários com paginação.
        
        Args:
            skip: Offset
            limit: Limite de registros
            
        Returns:
            Lista de usuários
        """
        return self.repo.list(skip=skip, limit=limit, order_by="createdAt", reverse=True)

    def list_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lista usuários por papel.
        
        Args:
            role: Papel (student, teacher, coordinator, admin)
            skip: Offset
            limit: Limite de registros
            
        Returns:
            Lista de usuários com o papel especificado
        """
        return self.repo.list_by_role(role, skip=skip, limit=limit)

    def list_users_by_status(self, status: AccessStatus, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lista usuários por status de acesso.
        
        Args:
            status: Status (active, inactive, suspended)
            skip: Offset
            limit: Limite de registros
            
        Returns:
            Lista de usuários com o status especificado
        """
        return self.repo.list_by_access_status(status, skip=skip, limit=limit)

    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """
        Atualiza um usuário com validações de negócio.
        
        Args:
            user_id: ID do usuário
            update_data: Dicionário com campos a atualizar
            
        Returns:
            Usuário atualizado ou None se não encontrado
            
        Raises:
            HTTPException: Se novos valores violam restrições únicas
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            return None
        
        # Validar matrícula se está sendo atualizada
        if "registration" in update_data and update_data["registration"] != user.registration:
            if self.repo.registration_exists(update_data["registration"], exclude_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nova matrícula já está em uso"
                )
        
        # Validar email se está sendo atualizado
        if "email" in update_data and update_data["email"] != user.email:
            if self.repo.email_exists(update_data["email"], exclude_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Novo email já está em uso"
                )
        
        return self.repo.update(user_id, update_data)

    def update_user_status(self, user_id: int, current_user: User, new_status: AccessStatus) -> Optional[User]:
        """
        Atualiza o status de acesso de um usuário com validações de autorização.
        
        Args:
            user_id: ID do usuário a atualizar
            current_user: Usuário que está fazendo a solicitação (para validar permissão)
            new_status: Novo status de acesso
            
        Returns:
            Usuário atualizado ou None se não encontrado
            
        Raises:
            HTTPException: Se usuário não tem permissão ou tenta alterar a si mesmo
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            return None
        
        # Impedir auto-alteração
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não é permitido alterar o próprio status de acesso"
            )
        
        return self.repo.update(user_id, {"accessStatus": new_status})

    def update_user_role(self, user_id: int, current_user: User, new_role: UserRole) -> Optional[User]:
        """
        Atualiza o papel de um usuário com validações de autorização.
        
        Args:
            user_id: ID do usuário a atualizar
            current_user: Usuário que está fazendo a solicitação
            new_role: Novo papel do usuário
            
        Returns:
            Usuário atualizado ou None se não encontrado
            
        Raises:
            HTTPException: Se usuário não tem permissão
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            return None
        
        # Impedir auto-alteração de papel
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não é permitido alterar o próprio papel"
            )
        
        # Coordenadores não podem alterar papéis de admin/coordenador
        if current_user.role == UserRole.coordinator:
            if new_role in [UserRole.admin, UserRole.coordinator]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Coordenadores não podem atribuir papéis de admin ou coordenador"
                )
        
        return self.repo.update(user_id, {"role": new_role})

    def delete_user(self, user_id: int) -> bool:
        """
        Deleta um usuário.
        
        Args:
            user_id: ID do usuário a deletar
            
        Returns:
            True se deletado, False se não encontrado
        """
        return self.repo.delete(user_id)

    def authenticate_user(self, registration: str, password: str) -> Optional[User]:
        """
        Autentica um usuário verificando matrícula e senha.
        
        Args:
            registration: Matrícula do usuário
            password: Senha em texto plano
            
        Returns:
            Usuário se autenticado com sucesso, None caso contrário
        """
        user = self.repo.get_by_registration(registration)
        if not user:
            return None
        
        if not verify_password(password, user.passwordHash):
            return None
        
        return user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Altera a senha de um usuário.
        
        Args:
            user_id: ID do usuário
            current_password: Senha atual em texto plano
            new_password: Nova senha em texto plano
            
        Returns:
            True se alterada com sucesso
            
        Raises:
            HTTPException: Se senha atual está incorreta ou usuário não encontrado
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar senha atual
        if not verify_password(current_password, user.passwordHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha atual incorreta"
            )
        
        # Atualizar com nova senha
        new_hashed = get_password_hash(new_password)
        return self.repo.update(user_id, {"passwordHash": new_hashed}) is not None

    def count_users(self) -> int:
        """
        Conta o total de usuários no sistema.
        
        Returns:
            Número total de usuários
        """
        return self.repo.count()

    def count_users_by_role(self, role: UserRole) -> int:
        """
        Conta usuários com um papel específico.
        
        Args:
            role: Papel do usuário
            
        Returns:
            Número de usuários com o papel
        """
        return self.repo.count_by_role(role)
