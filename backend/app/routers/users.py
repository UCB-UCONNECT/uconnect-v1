# ---------------- ROTAS DE GERENCIAMENTO DE USUÁRIOS ---------------- #
"""
Este arquivo define os endpoints da API para o
gerenciamento completo do ciclo de vida dos usuários.

Suas responsabilidades incluem:
- Criação (cadastro) de novos usuários.
- Operações CRUD administrativas para listar, visualizar, atualizar e deletar.
- Endpoints de "self-service" (`/me`) para que os usuários possam gerenciar
  seus próprios perfis.
- Rotas específicas e seguras (`PATCH`) para que administradores e
  coordenadores possam gerenciar status e papéis de outros usuários, com
  lógicas de permissão detalhadas.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..dependencies import require_roles, get_current_active_user
from ..core.security import get_password_hash
from ..models import User, Session, UserRole, AccessStatus
from ..schemas import UserResponse, UserCreate, UserUpdate, UserRoleUpdate
from .. import models, schemas
from ..services import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

# --- Configuração do Roteador de Usuários ---
# O `APIRouter` agrupa as rotas de gerenciamento de usuários sob o prefixo
# `/users` e a tag "users" na documentação da API.
router = APIRouter(prefix="/users", tags=["users"])

# --- Rota: Criar um Novo Usuário (Cadastro) ---
# Endpoint público para o cadastro de novos usuários. Verifica se a matrícula
# já existe e armazena a senha de forma segura (com hash).
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, service: UserService = Depends(get_user_service)):
    # Delegate creation logic to the service (handles validation and hashing)
    created = service.create_user(
        registration=user.registration,
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role,
    )
    return created

# --- Rota: Listar Todos os Usuários (Admin) ---
# Endpoint protegido (somente Admin) que retorna uma lista paginada de todos
# os usuários do sistema.
@router.get("/", response_model=list[schemas.UserResponse])
def read_users(
    skip: int = 0, limit: int = 100, service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    return service.list_users(skip=skip, limit=limit)

# --- Rota: Visualizar Próprio Perfil ---
# Endpoint para que um usuário autenticado possa obter seus próprios dados.
@router.get("/me", response_model=schemas.UserResponse)
def read_own_profile(current_user: models.User = Depends(get_current_active_user)):
    return current_user

# --- Rota: Atualizar Próprio Perfil ---
# Endpoint para que um usuário possa atualizar suas próprias informações.
# Campos sensíveis como `role` e `accessStatus` são ignorados por segurança.
@router.put("/me", response_model=schemas.UserResponse)
def update_own_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    update_data = user_update.dict(exclude_unset=True)
    update_data.pop("role", None)
    update_data.pop("accessStatus", None)

    # Delegate to service (it will validate unique constraints if needed)
    updated = service.update_user(current_user.id, update_data)
    return updated or current_user

# --- Rota: Atualizar Outro Usuário (Admin) ---
# Endpoint protegido (somente Admin) para atualizar os dados de qualquer
# usuário no sistema.
@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int, user_update: schemas.UserUpdate, service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    update_data = user_update.dict(exclude_unset=True)
    updated = service.update_user(user_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return updated

# --- Rota: Deletar um Usuário (Admin) ---
# Endpoint protegido (somente Admin) para remover um usuário. Também remove
# todas as sessões ativas associadas a esse usuário.
@router.delete("/{user_id}")
def delete_user(
    user_id: int, service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    deleted = service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Rota: Atualizar Status de Acesso (Admin) ---
# Endpoint específico (somente Admin) para alterar o status de um usuário
# (ativo, inativo, suspenso). Impede que um admin altere o próprio status.
@router.patch("/{user_id}/status", response_model=schemas.UserResponse)
def update_user_access_status(
    user_id: int, status_update: dict, service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    updated = service.update_user_status(user_id, current_user, status_update.get("accessStatus"))
    if not updated:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return updated

# --- Rota: Atualizar Papel do Usuário (Admin/Coordenador) ---
# Endpoint com lógica de permissão detalhada para alterar o papel de um
# usuário. Impede auto-alteração, alteração de outros admins e que
# coordenadores atribuam papéis de nível igual ou superior ao seu.
@router.patch("/{user_id}/role", response_model=schemas.UserResponse)
def update_user_role(
    user_id: int, role_update: schemas.UserRoleUpdate, service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    updated = service.update_user_role(user_id, current_user, role_update.role)
    if not updated:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return updated
