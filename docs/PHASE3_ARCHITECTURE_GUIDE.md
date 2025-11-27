# ARQUITETURA FASE 3 - CAMADAS DE REPOSITÓRIO E SERVIÇO

## Estrutura de Diretórios Criada

```
backend/app/
├── repositories/
│   ├── __init__.py              (imports públicos)
│   ├── base.py                  (GenericRepository - CRUD padrão)
│   ├── user.py                  (UserRepository - queries específicas de User)
│   └── event.py                 (EventRepository - queries específicas de Event)
│
├── services/
│   ├── __init__.py              (imports públicos)
│   └── user.py                  (UserService - lógica de negócio de User)
│
└── routers/
    ├── users.py                 (próximo para refatorar)
    ├── events.py
    ├── chat.py
    ├── groups.py
    ├── publications.py
    ├── notifications.py
    ├── access.py
    └── auth.py
```

---

## Padrão de Implementação

### 1. GenericRepository<T>

```python
class GenericRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T])
    
    # Operações CRUD padrão
    def create(obj_in: Dict) -> T
    def get_by_id(obj_id: int) -> Optional[T]
    def list(skip, limit, order_by, reverse) -> List[T]
    def update(obj_id: int, obj_in: Dict) -> Optional[T]
    def delete(obj_id: int) -> bool
    
    # Operações de busca
    def exists(**filters) -> bool
    def find_by_filter(**filters) -> Optional[T]
    def find_all_by_filter(skip, limit, **filters) -> List[T]
    
    # Operações de contagem
    def count(**filters) -> int
```

### 2. SpecificRepository (UserRepository exemplo)

```python
class UserRepository(GenericRepository[User]):
    def __init__(self, db: Session)
    
    # Métodos específicos de User
    def get_by_registration(registration: str) -> Optional[User]
    def get_by_email(email: str) -> Optional[User]
    def list_by_role(role: UserRole) -> List[User]
    def list_by_access_status(status: AccessStatus) -> List[User]
    def registration_exists(registration: str) -> bool
    def email_exists(email: str) -> bool
```

### 3. Service (UserService exemplo)

```python
class UserService:
    def __init__(self, db: Session)
    self.repository = UserRepository(db)
    
    # Lógica de negócio
    def create_user(...) -> User
    def authenticate_user(...) -> Optional[User]
    def update_user_status(...) -> Optional[User]
    def change_password(...) -> bool
    # ... mais 15+ métodos
```

---

## Fluxo de Dados Completo

### Exemplo: GET /api/v1/users/{user_id}

```
┌─────────────────────────────────────────────────────────────┐
│ HTTP GET /api/v1/users/123                                  │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Router Layer (HTTP)                                         │
│ @router.get("/{user_id}", response_model=UserResponse)     │
│                                                              │
│ Responsabilidades:                                          │
│  - Validar path parameter (user_id: int)                   │
│  - Validar autenticação/autorização                        │
│  - Converter response para schema                          │
└─────────────────────────────────────────────────────────────┘
                        ↓
            service = UserService(db)
            user = service.get_user_by_id(123)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Service Layer (Business Logic)                              │
│ def get_user_by_id(user_id: int) -> Optional[User]         │
│                                                              │
│ Responsabilidades:                                          │
│  - Aplicar regras de negócio                               │
│  - Validações de autorização                               │
│  - Orquestração (pode usar múltiplos repos)                │
│  - Tratamento de exceções de negócio                       │
└─────────────────────────────────────────────────────────────┘
                        ↓
            return self.repository.get_by_id(123)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Repository Layer (Data Access)                              │
│ def get_by_id(obj_id: int) -> Optional[T]                  │
│                                                              │
│ Responsabilidades:                                          │
│  - Queries ao BD (SQLAlchemy)                              │
│  - Operações CRUD                                          │
│  - Conversão ORM ↔ Python                                  │
└─────────────────────────────────────────────────────────────┘
                        ↓
    self.db.query(User).filter(User.id == 123).first()
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Database                                                    │
│ SELECT * FROM User WHERE id = 123;                         │
└─────────────────────────────────────────────────────────────┘
                        ↓
            User(id=123, name="João", ...)
                        ↓
        Repository → Service → Router
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ HTTP Response                                               │
│ {                                                           │
│   "id": 123,                                                │
│   "registration": "2023001",                               │
│   "name": "João",                                           │
│   "email": "joao@example.com",                             │
│   "role": "student",                                        │
│   "accessStatus": "active",                                │
│   "createdAt": "2025-11-26T10:00:00"                       │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Comparação: Antes x Depois

### Acesso Direto (Antes - Ruim)

```python
# router/users.py
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    # Lógica de BD misturada com HTTP
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(404, "Não encontrado")
    return db_user

# Problemas:
# - Teste requer BD real
# - Lógica de BD no router
# - Difícil reutilizar (CLI, cron jobs, etc)
# - Sem validações centralizadas
```

### Com Serviço (Depois - Bom)

```python
# router/users.py
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(404, "Não encontrado")
    
    return user

# Benefícios:
# - Router focado em HTTP
# - Serviço testável com mock
# - Lógica reutilizável
# - Validações centralizadas
```

---

## Classes Hierárquicas

```
GenericRepository[T]
    │
    ├── UserRepository
    │   ├── Herda: create, get_by_id, list, update, delete, ...
    │   └── Adiciona: get_by_registration, list_by_role, ...
    │
    └── EventRepository
        ├── Herda: create, get_by_id, list, update, delete, ...
        └── Adiciona: get_by_creator, get_upcoming_events, ...

Service
    │
    └── UserService
        ├── Usa: UserRepository
        └── Métodos: create_user, authenticate_user, ...
```

---

## Métodos Públicos por Classe

### GenericRepository (8 métodos)
1. create(obj_in)
2. get_by_id(obj_id)
3. list(skip, limit, order_by, reverse)
4. update(obj_id, obj_in)
5. delete(obj_id)
6. exists(**filters)
7. find_by_filter(**filters)
8. find_all_by_filter(skip, limit, **filters)
9. count(**filters)

### UserRepository (8 + 9 = 17 métodos)
Herdados: create, get_by_id, list, update, delete, exists, find_by_filter, find_all_by_filter, count

Próprios:
1. get_by_registration(registration)
2. get_by_email(email)
3. list_by_role(role, skip, limit)
4. list_by_access_status(status, skip, limit)
5. registration_exists(registration, exclude_id)
6. email_exists(email, exclude_id)
7. count_by_role(role)
8. count_by_status(status)

### UserService (15+ métodos)
1. create_user(registration, name, email, password, role)
2. get_user_by_id(user_id)
3. get_user_by_registration(registration)
4. get_user_by_email(email)
5. list_users(skip, limit)
6. list_users_by_role(role, skip, limit)
7. list_users_by_status(status, skip, limit)
8. update_user(user_id, update_data)
9. update_user_status(user_id, current_user, new_status)
10. update_user_role(user_id, current_user, new_role)
11. delete_user(user_id)
12. authenticate_user(registration, password)
13. change_password(user_id, current_password, new_password)
14. count_users()
15. count_users_by_role(role)

---

## Testabilidade

### Teste do Repositório
```python
def test_get_user_by_registration():
    db = create_test_db()  # SQLite em memória
    repo = UserRepository(db)
    
    user = repo.create({...})
    found = repo.get_by_registration(user.registration)
    
    assert found is not None
    assert found.id == user.id
```

### Teste do Serviço
```python
def test_create_user_duplicate():
    db = create_test_db()
    service = UserService(db)
    
    service.create_user("2023001", "João", ...)
    
    with pytest.raises(HTTPException) as exc:
        service.create_user("2023001", "Pedro", ...)
    
    assert exc.value.status_code == 400
```

### Teste do Router (futura)
```python
def test_get_user_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/users/123")
    assert response.status_code == 200
    assert response.json()["id"] == 123
```
