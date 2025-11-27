"""
Camada de Serviços (Services Layer)

A camada de serviços orquestra a lógica de negócio utilizando repositórios.
Esta é uma camada intermediária entre os routers e os repositórios.

Responsabilidades:
- Orquestração de operações multi-repositório
- Validação e lógica de negócio complexa
- Tratamento de exceções de negócio
- Garantir integridade de dados
- Implementar regras de autorização

Fluxo de dados:
Router -> Service -> Repository -> Database
         ^                            |
         |____________________________|

Benefícios:
- Routers ficam simples (apenas HTTP)
- Lógica de negócio centralizada
- Fácil de testar
- Facilita reuso de lógica entre endpoints
"""

from .user import UserService
from .event import EventService
from .academic_group import AcademicGroupService
from .post import PostService
from .announcement import AnnouncementService
from .conversation import ConversationService
from .message import MessageService
from .auth import AuthService
from .access import AccessService

__all__ = [
    "UserService",
    "EventService",
    "AcademicGroupService",
    "PostService",
    "AnnouncementService",
    "ConversationService",
    "MessageService",
    "AuthService",
    "AccessService",
]
