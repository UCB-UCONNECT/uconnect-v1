Phase 3: Service + Repository refactor, tests and router updates

Summary:
- Implementa `GenericRepository` e repositórios específicos (User, Event, Post, Announcement, AcademicGroup, Conversation, Message, Access).
- Cria camada de `services` para orquestrar lógica de negócio (UserService, EventService, PostService, AnnouncementService, AcademicGroupService, ConversationService, MessageService, AccessService, AuthService).
- Refatora routers para depender de services (events, users, groups, publications, chat, notifications, access, auth).
- Adiciona testes unitários em memória para serviços e repositórios: `tests/test_user_service.py`, `tests/test_event_service.py`, `tests/test_post_service.py`, `tests/test_academic_group_service.py`.

Why:
- Separação clara entre HTTP (routers), regras de negócio (services) e acesso a dados (repositories).
- Facilita testes, manutenção e futuras migrações de BD.

Breaking changes / notes:
- Nenhuma alteração nas rotas públicas (mesmas URLs/JSON). Alguns modelos internos e enums receberam aliases de compatibilidade para manter fixtures existentes.
- Warnings de depreciação (SQLAlchemy/Pydantic) não bloqueiam execução.

Suggested PR title:
"Phase 3 — Introduce Service/Repository layers; refactor routers; add unit tests"

Suggested PR body (short):
Implement Service and Repository layers, refactor existing routers to use services, and add unit tests for core services and repositories. This centralizes business logic and improves testability.

Files of interest:
- `backend/app/repositories/*`
- `backend/app/services/*`
- `backend/app/routers/*` (refactored)
- `tests/test_*_service.py` (new)
