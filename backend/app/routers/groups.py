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
from ..db import get_db
from .. import schemas, models
from ..utils import require_roles

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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    db_group = models.AcademicGroup(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

# --- Rota: Listar Todos os Grupos Acadêmicos ---
# Endpoint protegido (Admin/Coordenador) que retorna uma lista de todos os
# grupos acadêmicos cadastrados.
@router.get("/", response_model=list[schemas.AcademicGroupResponse])
def get_all_groups(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    return db.query(models.AcademicGroup).all()

# --- Rota: Obter Detalhes de um Grupo ---
# Endpoint protegido (Admin/Coordenador/Professor) que retorna as informações
# detalhadas de um grupo, incluindo a lista de usuários membros.
@router.get("/{group_id}", response_model=schemas.AcademicGroupDetailResponse)
def get_group_details(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "coordinator", "teacher"]))
):
    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    
    update_data = group_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_group, key, value)
        
    db.commit()
    db.refresh(db_group)
    return db_group

# --- Rota: Deletar um Grupo Acadêmico ---
# Endpoint protegido (somente Admin) para remover um grupo do banco de dados.
@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    
    db.delete(db_group)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Rota: Adicionar Usuário a um Grupo ---
# Endpoint protegido (Admin/Coordenador) para associar um usuário a um grupo,
# adicionando-o à lista de membros. Previne duplicatas.
@router.post("/{group_id}/users/{user_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.AcademicGroupDetailResponse)
def add_user_to_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if db_user in db_group.users:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já pertence a este grupo")

    db_group.users.append(db_user)
    db.commit()
    db.refresh(db_group)
    return db_group

# --- Rota: Remover Usuário de um Grupo ---
# Endpoint protegido (Admin/Coordenador) para desassociar um usuário de um
# grupo, removendo-o da lista de membros.
@router.delete("/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "coordinator"]))
):
    db_group = db.query(models.AcademicGroup).filter(models.AcademicGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    if db_user not in db_group.users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não pertence a este grupo")

    db_group.users.remove(db_user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
