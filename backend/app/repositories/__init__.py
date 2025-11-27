"""
Camada de Repositório - Padrão Repository Pattern

Esta camada fornece abstração para acesso a dados, desacoplando a lógica de negócio
das operações diretas com o banco de dados (SQLAlchemy).

Arquitetura:
- GenericRepository: Classe base com operações CRUD padrão para todas as entidades
- SpecificRepository: Repositórios específicos estendendo GenericRepository com lógica customizada
- Services: Orquestram lógica de negócio utilizando repositórios

Benefícios:
- Facilita testes unitários (mocking de repositórios)
- Melhora manutenibilidade (lógica de acesso centralizada)
- Permite trocar implementação de BD sem afetar lógica de negócio
- Código mais limpo nos routers (chamam serviços, não BD direto)
"""

from .base import GenericRepository
from .user import UserRepository
from .event import EventRepository
from .academic_group import AcademicGroupRepository
from .post import PostRepository
from .announcement import AnnouncementRepository
from .conversation import ConversationRepository
from .message import MessageRepository
from .access import AccessRepository

__all__ = [
	"GenericRepository",
	"UserRepository",
	"EventRepository",
	"AcademicGroupRepository",
	"PostRepository",
	"AnnouncementRepository",
	"ConversationRepository",
	"MessageRepository",
	"AccessRepository",
]
