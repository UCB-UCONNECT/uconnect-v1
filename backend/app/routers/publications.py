# ---------------- ROTAS DE PUBLICAÇÕES (POSTS) ---------------- #
"""
Este arquivo define os endpoints da API para o
gerenciamento de publicações (posts) globais, funcionando como um mural de
avisos ou feed de notícias.

Suas responsabilidades incluem:
- Permitir que usuários autorizados (professores, coordenadores, admins)
  criem novas publicações.
- Fornecer uma lista de todas as publicações para qualquer usuário autenticado.
- Permitir a edição e exclusão de publicações, com uma regra de permissão
  que libera a ação para o autor original ou para usuários com papéis
  privilegiados (coordenador, admin).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from .. import schemas, models
from ..utils import require_roles

# --- Configuração do Roteador de Publicações ---
# O `APIRouter` agrupa as rotas de gerenciamento de publicações sob o
# prefixo `/posts` e a tag "Publications" na documentação da API.
router = APIRouter(
    prefix="/posts",
    tags=["Publications"]
)

# --- Rota: Criar Nova Publicação ---
# Endpoint protegido (Professor/Coordenador/Admin) para criar uma nova
# publicação. O autor é automaticamente definido como o usuário logado.
@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    new_post = models.Post(title=post.title, content=post.content, authorId=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# --- Rota: Listar Todas as Publicações ---
# Endpoint que retorna uma lista de todas as publicações, ordenadas da mais
# recente para a mais antiga. Acessível a todos os usuários logados.
@router.get("/", response_model=List[schemas.PostResponse])
def get_all_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["student", "teacher", "coordinator", "admin"]))
):
    posts = db.query(models.Post).order_by(models.Post.date.desc()).all()
    return posts

# --- Rota: Editar uma Publicação ---
# Endpoint protegido para atualizar o conteúdo de uma publicação. A permissão
# é concedida se o usuário for o autor original ou um Coordenador/Admin.
@router.patch("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada")

    is_author = db_post.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não tem permissão para editar esta publicação")
    
    update_data = post_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

# --- Rota: Deletar uma Publicação ---
# Endpoint protegido para remover uma publicação. Segue a mesma lógica de
# permissão da rota de edição: apenas o autor ou um Coordenador/Admin
# pode deletar o post.
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada")
    
    is_author = db_post.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Não tem permissão para deletar esta publicação")

    db.delete(db_post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
