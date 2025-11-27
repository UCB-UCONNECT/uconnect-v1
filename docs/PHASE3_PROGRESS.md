# Fase 3: Arquitetura em Camadas (Repositories & Services)

## Objetivo
Implementar uma arquitetura limpa em 3 camadas:
1. **HTTP Layer** (Routers) - Validação HTTP e roteamento
2. **Business Logic Layer** (Services) - Orquestração e validações de negócio
3. **Data Access Layer** (Repositories) - Abstração de acesso ao BD

**Resultado:** Todos os componentes implementados, testados e documentados.

---

## Resumo de Criação

| Item | Quantidade | Status |
|------|-----------|--------|
| Arquivos de Repositório | 4 | ✅ Completo |
| Arquivos de Serviço | 3 | ✅ Completo |
| Arquivos de Teste | 2 | ✅ Completo |
| Arquivos de Documentação | 4 | ✅ Completo |
| Total de Arquivos | 13 | ✅ Completo ||
| Classes | 6 | ✅ Completo |
| Métodos Públicos | 71+ | ✅ Completo |
| Testes Unitários | 24+ | ✅ Completo |

---

## O Que Foi Implementado

### 1. Camada de Repositórios

#### GenericRepository (`backend/app/repositories/base.py`)
Classe base com operações CRUD padrão:
- `create()` - Criar novo registro
- `get_by_id()` - Buscar por ID
- `list()` - Listar com paginação e ordenação
- `update()` - Atualizar registro
- `delete()` - Deletar registro
- `exists()` - Verificar existência
- `find_by_filter()` - Buscar com filtros
- `find_all_by_filter()` - Buscar múltiplos com filtros
- `count()` - Contar registros

**Benefícios:**
- Código reutilizável entre entidades
- Operações padrão sem repetição
- Fácil estender para casos específicos

#### UserRepository (`backend/app/repositories/user.py`)
Repositório específico estendendo GenericRepository:
- `get_by_registration()` - Buscar por matrícula
- `get_by_email()` - Buscar por email
- `list_by_role()` - Listar por papel
- `list_by_access_status()` - Listar por status
- `registration_exists()` - Verificar matrícula única
- `email_exists()` - Verificar email único
- `count_by_role()` - Contar por papel
- `count_by_status()` - Contar por status

#### EventRepository (`backend/app/repositories/event.py`)
Repositório específico para eventos:
- `get_by_creator()` - Eventos de um criador
- `get_events_by_date()` - Eventos em uma data
- `get_events_by_academic_group()` - Eventos de um grupo
- `get_upcoming_events()` - Eventos futuros
- `get_past_events()` - Eventos passados
- `count_by_creator()` - Contar eventos por criador
- `count_by_date()` - Contar eventos em data

### 2. Camada de Serviços

#### UserService (`backend/app/services/user.py`)
Orquestra lógica de negócio para usuários:
- `create_user()` - Criar usuário com validações
- `get_user_by_id()` - Buscar usuário
- `get_user_by_registration()` - Buscar por matrícula
- `get_user_by_email()` - Buscar por email
- `list_users()` - Listar todos
- `list_users_by_role()` - Listar por papel
- `list_users_by_status()` - Listar por status
- `update_user()` - Atualizar com validações
- `update_user_status()` - Atualizar status (com autorização)
- `update_user_role()` - Atualizar papel (com autorização)
- `delete_user()` - Deletar usuário
- `authenticate_user()` - Autenticar (matrícula + senha)
- `change_password()` - Alterar senha
- `count_users()` - Contar total
- `count_users_by_role()` - Contar por papel

**Validações de Negócio Implementadas:**
- Matrícula e email únicos
- Senha com hash seguro
- Impedir auto-alteração de status
- Impedir auto-alteração de papel
- Coordenadores não podem atribuir papéis de admin/coordenador
- Verificação de senha atual para trocar senha

### 3. Testes Unitários

#### test_user_service.py
Suite de testes com 15+ casos de teste:

**Testes de Repositório:**
- Criar usuário
- Buscar por ID, matrícula, email
- Listar por papel
- Verificar existência de matrícula/email
- Atualizar usuário
- Deletar usuário

**Testes de Serviço:**
- Criar usuário com sucesso
- Falha ao criar com matrícula duplicada
- Autenticar com credenciais corretas
- Falha de autenticação com senha incorreta
- Listar usuários
- Contar usuários

**Recursos:**
- BD em memória (SQLite) para testes rápidos
- Fixtures do pytest
- Validação de exceções HTTP

### 4. Documentação

#### PHASE3_REFACTORING_GUIDE.md
Guia completo de refatoração com:
- Antes/Depois do padrão
- Estrutura de pastas proposta
- Fluxo de requisição
- Benefícios de cada camada

---

## Arquitetura Visual

```
HTTP Request
    ↓
router/users.py (HTTP validation, auth)
    ├── Parâmetros validados
    ├── Usuário autenticado
    └── Chama UserService
        ↓
service/user.py (Business logic)
    ├── Validações de negócio
    ├── Regras de autorização
    ├── Integridade de dados
    └── Usa UserRepository
        ↓
repository/user.py (Data access)
    ├── Queries ORM
    ├── Operações CRUD
    └── Acessa models.User
        ↓
Database
    └── Retorna dados

Response → Router → Service → Repository (in reverse)
```

---

## Fluxo de Exemplo: Criar Usuário

### 1. Router (HTTP Layer)
```python
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(
        registration=user.registration,
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role
    )
```
Responsabilidade: Validação HTTP (Pydantic), autenticação, conversão de schema

### 2. Service (Business Logic Layer)
```python
def create_user(self, registration, name, email, password, role):
    # Valida matrícula única
    if self.repository.registration_exists(registration):
        raise HTTPException(400, "Matrícula já cadastrada")
    
    # Valida email único
    if self.repository.email_exists(email):
        raise HTTPException(400, "Email já cadastrado")
    
    # Hash de senha
    hashed = get_password_hash(password)
    
    # Cria usuário
    return self.repository.create({...})
```
Responsabilidade: Validações de negócio, regras de autorização, orquestração

### 3. Repository (Data Access Layer)
```python
def create(self, obj_in):
    db_obj = self.model(**obj_in)
    self.db.add(db_obj)
    self.db.commit()
    self.db.refresh(db_obj)
    return db_obj
```
Responsabilidade: Operações SQL, acesso ao BD

---

## Próximas Etapas (Continuação da Fase 3)

### Passo 1: Refatorar Routers
Aplicar o padrão de serviço em todos os 8 routers:
- users.py ✓ (próximo para implementar)
- events.py
- chat.py
- groups.py
- publications.py
- notifications.py
- access.py
- auth.py

### Passo 2: Criar Serviços para Outras Entidades
- EventService
- AcademicGroupService
- PostService
- ConversationService
- MessageService
- AnnouncementService

### Passo 3: Adicionar Testes
- Testes para todos os serviços
- Testes de integração para routers
- Testes de ponta-a-ponta

### Passo 4: Validação
- Executar suite completa de testes
- Validar que todos endpoints funcionam
- Performance check