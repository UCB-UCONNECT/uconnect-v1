# Exemplo de Refatoração de Router com Serviços

## Antes (Acesso Direto ao BD)

```python
# routers/users.py (ANTES)
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.registration == user.registration).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já cadastrado")

    hashed_password = get_password_hash(user.password)

    db_user = models.User(
        registration=user.registration,
        name=user.name,
        email=user.email,
        passwordHash=hashed_password,
        role=user.role,
        accessStatus=models.AccessStatus.active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

### Problemas:
- Lógica de negócio misturada com HTTP
- Difícil testar (precisa mockar BD)
- Código repetido em outros endpoints
- Não segue separação de responsabilidades

---

## Depois (Com Serviço)

```python
# routers/users.py (DEPOIS)
from ..services import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    service = UserService(db)
    return service.create_user(
        registration=user.registration,
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role
    )


@router.get("/", response_model=list[schemas.UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    service = UserService(db)
    return service.list_users(skip=skip, limit=limit)


@router.get("/me", response_model=schemas.UserResponse)
def read_own_profile(current_user: models.User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_own_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    
    update_data = user_update.dict(exclude_unset=True)
    # Impedir auto-atribuição de papel/status
    update_data.pop("role", None)
    update_data.pop("accessStatus", None)
    
    return service.update_user(current_user.id, update_data)


@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    service = UserService(db)
    updated_user = service.update_user(user_id, user_update.dict(exclude_unset=True))
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return updated_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    service = UserService(db)
    
    if not service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{user_id}/status", response_model=schemas.UserResponse)
def update_user_access_status(
    user_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    service = UserService(db)
    updated_user = service.update_user_status(
        user_id,
        current_user,
        status_update["accessStatus"]
    )
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return updated_user
```

### Benefícios:
- Router focado apenas em HTTP (request/response)
- Lógica de negócio centralizada no serviço
- Fácil testar (mock do serviço)
- Código reutilizável (serviço pode ser usado por CLI, cron jobs, etc)
- Validações de negócio no lugar correto

---

## Estrutura de Pastas (Fase 3)

```
backend/app/
├── routers/               (HTTP Layer - Controllers)
│   ├── users.py          (endpoint definitions)
│   ├── events.py
│   └── ...
├── services/              (Business Logic Layer)
│   ├── user.py           (orchestration, validations)
│   ├── event.py
│   └── ...
├── repositories/          (Data Access Layer)
│   ├── base.py           (generic CRUD)
│   ├── user.py           (user-specific queries)
│   ├── event.py
│   └── ...
├── models.py             (ORM definitions)
├── schemas.py            (Pydantic validation)
└── db/                   (Database config)
    ├── session.py
    └── base.py
```

---

## Fluxo de Requisição

```
HTTP Request
    ↓
Router (HTTP validation, auth)
    ↓
Service (Business logic, validations)
    ↓
Repository (Database queries)
    ↓
Database
    ↓
Repository (returns ORM object)
    ↓
Service (processes result)
    ↓
Router (converts to schema/response)
    ↓
HTTP Response
```
