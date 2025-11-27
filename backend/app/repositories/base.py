"""
GenericRepository - Classe Base com Operações CRUD Padrão

Implementa o padrão Repository Pattern fornecendo uma abstração
para operações de banco de dados comuns a todas as entidades.

Métodos Fornecidos:
- create(): Criar um novo registro
- get_by_id(): Buscar por ID
- list(): Listar com paginação
- update(): Atualizar registro
- delete(): Deletar registro
- exists(): Verificar existência
"""

from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

T = TypeVar("T")


class GenericRepository(Generic[T]):
    """
    Repositório genérico para operações CRUD básicas.
    
    Type Parameter:
        T: Tipo da entidade ORM (User, Event, etc)
    
    Exemplo de uso:
        repo = GenericRepository(db, User)
        user = repo.create({"name": "João", "email": "joao@example.com"})
        users = repo.list(skip=0, limit=10)
    """

    def __init__(self, db: Session, model: Type[T]):
        """
        Inicializa o repositório com sessão de BD e modelo ORM.
        
        Args:
            db: Sessão SQLAlchemy ativa
            model: Classe de modelo ORM (ex: User, Event)
        """
        self.db = db
        self.model = model

    def create(self, obj_in: Dict[str, Any]) -> T:
        """
        Cria um novo registro no banco de dados.
        
        Args:
            obj_in: Dicionário com dados do novo objeto
            
        Returns:
            Instância do modelo criado
            
        Exemplo:
            user = repo.create({"name": "João", "email": "joao@example.com"})
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, obj_id: int) -> Optional[T]:
        """
        Busca um registro pelo ID.
        
        Args:
            obj_id: ID do objeto a buscar
            
        Returns:
            Instância do modelo ou None se não encontrado
        """
        return self.db.query(self.model).filter(self.model.id == obj_id).first()

    def list(self, skip: int = 0, limit: int = 100, order_by: Optional[str] = None, reverse: bool = False) -> List[T]:
        """
        Lista registros com paginação.
        
        Args:
            skip: Número de registros a pular (offset)
            limit: Número máximo de registros a retornar
            order_by: Nome do campo para ordenação (opcional)
            reverse: Se True, ordena em ordem decrescente
            
        Returns:
            Lista de instâncias do modelo
            
        Exemplo:
            users = repo.list(skip=0, limit=10, order_by="createdAt", reverse=True)
        """
        query = self.db.query(self.model)
        
        if order_by:
            order_column = getattr(self.model, order_by, None)
            if order_column:
                order_column = desc(order_column) if reverse else asc(order_column)
                query = query.order_by(order_column)
        
        return query.offset(skip).limit(limit).all()

    def update(self, obj_id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        """
        Atualiza um registro existente.
        
        Args:
            obj_id: ID do objeto a atualizar
            obj_in: Dicionário com novos valores
            
        Returns:
            Instância atualizada ou None se não encontrado
            
        Exemplo:
            user = repo.update(1, {"name": "João Silva"})
        """
        db_obj = self.get_by_id(obj_id)
        if not db_obj:
            return None
        
        for field, value in obj_in.items():
            if value is not None and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, obj_id: int) -> bool:
        """
        Deleta um registro do banco de dados.
        
        Args:
            obj_id: ID do objeto a deletar
            
        Returns:
            True se deletado com sucesso, False se não encontrado
            
        Exemplo:
            success = repo.delete(1)
        """
        db_obj = self.get_by_id(obj_id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def exists(self, **filters: Any) -> bool:
        """
        Verifica se um registro com os filtros fornecidos existe.
        
        Args:
            **filters: Filtros como argumentos nomeados (ex: registration="12345")
            
        Returns:
            True se encontrado, False caso contrário
            
        Exemplo:
            exists = repo.exists(registration="12345", email="joao@example.com")
        """
        query = self.db.query(self.model)
        
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        
        return query.first() is not None

    def find_by_filter(self, **filters: Any) -> Optional[T]:
        """
        Busca um registro pelo primeiro filtro que corresponder.
        
        Args:
            **filters: Filtros como argumentos nomeados
            
        Returns:
            Primeira instância encontrada ou None
            
        Exemplo:
            user = repo.find_by_filter(email="joao@example.com")
        """
        query = self.db.query(self.model)
        
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        
        return query.first()

    def find_all_by_filter(self, skip: int = 0, limit: int = 100, **filters: Any) -> List[T]:
        """
        Busca todos os registros que correspondem aos filtros.
        
        Args:
            skip: Offset para paginação
            limit: Limite de registros
            **filters: Filtros como argumentos nomeados
            
        Returns:
            Lista de instâncias encontradas
            
        Exemplo:
            active_users = repo.find_all_by_filter(accessStatus="active")
        """
        query = self.db.query(self.model)
        
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()

    def count(self, **filters: Any) -> int:
        """
        Conta registros com filtros opcionais.
        
        Args:
            **filters: Filtros como argumentos nomeados
            
        Returns:
            Número total de registros encontrados
            
        Exemplo:
            total = repo.count(accessStatus="active")
        """
        query = self.db.query(self.model)
        
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        
        return query.count()
