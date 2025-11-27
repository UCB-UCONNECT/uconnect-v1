from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from ..db.session import get_db
from ..dependencies import require_roles
from ..models import AccessManager, User
from ..schemas import AccessManagerResponse, AccessManagerCreate, AccessManagerUpdate
from .. import models, schemas
from ..services import AccessService


def get_access_service(db: Session = Depends(get_db)) -> AccessService:
    return AccessService(db)

router = APIRouter(
    prefix="/access",
    tags=["Access Manager"]
)

# -------------------------
# Criar permissão para um usuário
# -------------------------
@router.post("/", response_model=schemas.AccessManagerResponse, status_code=status.HTTP_201_CREATED)
def create_access(
    access_data: schemas.AccessManagerCreate,
    service: AccessService = Depends(get_access_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    return service.create_access(access_data.dict())


# -------------------------
# Listar permissões de um usuário
# -------------------------
@router.get("/user/{user_id}", response_model=list[schemas.AccessManagerResponse])
def list_user_permissions(
    user_id: int,
    service: AccessService = Depends(get_access_service),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    return service.list_user_permissions(user_id)


# -------------------------
# Listar todas as permissões do sistema
# -------------------------
@router.get("/", response_model=list[schemas.AccessManagerResponse])
def list_all_permissions(
    service: AccessService = Depends(get_access_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    return service.list_all_permissions()


# -------------------------
# Atualizar uma permissão
# -------------------------
@router.patch("/{access_id}", response_model=schemas.AccessManagerResponse)
def update_permission(
    access_id: int,
    access_update: schemas.AccessManagerUpdate,
    service: AccessService = Depends(get_access_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    updated = service.update_permission(access_id, access_update.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de acesso não encontrado")
    return updated


# -------------------------
# Deletar permissão
# -------------------------
@router.delete("/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    access_id: int,
    service: AccessService = Depends(get_access_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    deleted = service.delete_permission(access_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de acesso não encontrado")
    return {"message": "Permissão removida"}


# -------------------------
# Verificar se usuário possui uma permissão
# -------------------------
@router.get("/check/{user_id}/{permission}")
def check_permission(
    user_id: int,
    permission: str,
    service: AccessService = Depends(get_access_service),
    current_user: models.User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    return {"has_permission": service.check_permission(user_id, permission)}
