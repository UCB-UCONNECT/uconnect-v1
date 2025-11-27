# ---------------- ROTAS DE GRUPOS ACADÊMICOS ---------------- #
"""
Este arquivo (routers/groups.py) define os endpoints da API para gerenciar
os Grupos Acadêmicos e seus membros.

Suas responsabilidades incluem:
- Operações CRUD (Criar, Ler, Atualizar, Deletar) para os grupos.
- Endpoints específicos para adicionar e remover usuários de um grupo,
  gerenciando o relacionamento muitos-para-muitos.
- Controle de acesso rigoroso baseado em papéis (roles), onde a maioria das
  operações é restrita a administradores e coordenadores.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..dependencies import require_roles
from ..models import User, AcademicGroup
from ..schemas import AcademicGroupResponse, AcademicGroupCreate, AcademicGroupUpdate, AcademicGroupDetailResponse
from .. import models, schemas
from ..services import AcademicGroupService


def get_academic_group_service(db: Session = Depends(get_db)) -> AcademicGroupService:
    return AcademicGroupService(db)

# --- Configuração do Roteador de Grupos ---
# O `APIRouter` agrupa as rotas de gerenciamento de grupos sob o prefixo
# `/groups` e a tag "Groups" na documentação da API.
router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

# --- Rota: Criar um Novo Grupo Acadêmico ---
# Endpoint protegido (somente Admin) para criar um novo grupo no sistema.
@router.post("/", response_model=schemas.AcademicGroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group: schemas.AcademicGroupCreate,
    service: AcademicGroupService = Depends(get_academic_group_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    created = service.create_group(group.dict())
    return created

# --- Rota: Listar Todos os Grupos Acadêmicos ---
# Endpoint protegido (Admin/Coordenador) que retorna uma lista de todos os
# grupos acadêmicos cadastrados.
@router.get("/", response_model=list[schemas.AcademicGroupResponse])
def get_all_groups(
    service: AcademicGroupService = Depends(get_academic_group_service),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    return service.list_groups()

# --- Rota: Obter Detalhes de um Grupo ---
# Endpoint protegido (Admin/Coordenador/Professor) que retorna as informações
# detalhadas de um grupo, incluindo a lista de usuários membros.
@router.get("/{group_id}", response_model=schemas.AcademicGroupDetailResponse)
def get_group_details(
    group_id: int,
    service: AcademicGroupService = Depends(get_academic_group_service),
    current_user: models.User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    db_group = service.get_group(group_id)
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    return db_group

# --- Rota: Atualizar um Grupo Acadêmico ---
# Endpoint protegido (somente Admin) para atualizar parcialmente as
# informações de um grupo existente. Utiliza o método PATCH.
@router.patch("/{group_id}", response_model=schemas.AcademicGroupResponse)
def update_group(
    group_id: int,
    group_update: schemas.AcademicGroupUpdate,
    service: AcademicGroupService = Depends(get_academic_group_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    update_data = group_update.dict(exclude_unset=True)
    updated = service.update_group(group_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    return updated

# --- Rota: Deletar um Grupo Acadêmico ---
# Endpoint protegido (somente Admin) para remover um grupo do banco de dados.
@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    service: AcademicGroupService = Depends(get_academic_group_service),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    deleted = service.delete_group(group_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Rota: Adicionar Usuário a um Grupo ---
# Endpoint protegido (Admin/Coordenador) para associar um usuário a um grupo,
# adicionando-o à lista de membros. Previne duplicatas.
@router.post("/{group_id}/users/{user_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.AcademicGroupDetailResponse)
def add_user_to_group(
    group_id: int,
    user_id: int,
    service: AcademicGroupService = Depends(get_academic_group_service),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    group = service.add_user_to_group(group_id, user_id)
    if group is None:
        # determine if group or user not found
        # check existence
        if not service.get_group(group_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return group

# --- Rota: Remover Usuário de um Grupo ---
# Endpoint protegido (Admin/Coordenador) para desassociar um usuário de um
# grupo, removendo-o da lista de membros.
@router.delete("/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_group(
    group_id: int,
    user_id: int,
    service: AcademicGroupService = Depends(get_academic_group_service),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    removed = service.remove_user_from_group(group_id, user_id)
    if not removed:
        # check why
        if not service.get_group(group_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
        # if group exists but removal failed, user likely not found or not member
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado ou não pertence a este grupo")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
