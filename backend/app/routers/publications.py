from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.session import get_db
from ..dependencies import require_roles, get_current_active_user
from ..models import UserRole
from .. import models, schemas
from ..services import PostService, AnnouncementService
from .notifications import notify_new_announcement


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)


def get_announcement_service(db: Session = Depends(get_db)) -> AnnouncementService:
    return AnnouncementService(db)

# Roteador principal que será exportado e importado no main.py
router = APIRouter(prefix="/publications", tags=["Publications"])

# --- 1. Roteador para Posts (Comunicados) ---
posts_router = APIRouter(prefix="/posts", tags=["Posts (Comunicados)"])

@posts_router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: schemas.PostCreate,
    service: PostService = Depends(get_post_service),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    payload = {**post.dict(), "authorId": current_user.id}
    created = service.create_post(payload)
    return created

@posts_router.get("/", response_model=List[schemas.PostResponse])
def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: PostService = Depends(get_post_service),
    current_user: models.User = Depends(get_current_active_user)
):
    return service.list_posts(skip=skip, limit=limit)

@posts_router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user: models.User = Depends(get_current_active_user)
):
    post = service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comunicado não encontrado"
        )
    return post

@posts_router.patch("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    service: PostService = Depends(get_post_service),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    db_post = service.get_post(post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comunicado não encontrado"
        )

    is_author = db_post.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar"
        )

    update_data = post_update.dict(exclude_unset=True)
    updated = service.update_post(post_id, update_data)
    return updated

@posts_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    db_post = service.get_post(post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comunicado não encontrado"
        )

    is_author = db_post.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar"
        )

    success = service.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao deletar comunicado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@posts_router.get("/stats/count")
def get_posts_count(
    service: PostService = Depends(get_post_service),
    current_user: models.User = Depends(get_current_active_user)
):
    total = service.repo.count()
    return {"total": total}


# --- 2. Roteador para Announcements (Avisos) ---
announcements_router = APIRouter(prefix="/announcements", tags=["Announcements (Avisos)"])

@announcements_router.post("/", response_model=schemas.AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement: schemas.AnnouncementCreate,
    service: AnnouncementService = Depends(get_announcement_service),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    payload = {**announcement.dict(), "authorId": current_user.id}
    created = service.create_announcement(payload)

    # Notificação adicionada no local correto
    await notify_new_announcement(created.id, created.title, current_user.name, service.db)
    return created

@announcements_router.get("/", response_model=List[schemas.AnnouncementResponse])
def get_all_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: AnnouncementService = Depends(get_announcement_service),
    current_user: models.User = Depends(get_current_active_user)
):
    return service.list_announcements(skip=skip, limit=limit)

@announcements_router.get("/{announcement_id}", response_model=schemas.AnnouncementResponse)
def get_announcement(
    announcement_id: int,
    service: AnnouncementService = Depends(get_announcement_service),
    current_user: models.User = Depends(get_current_active_user)
):
    announcement = service.get_announcement(announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso não encontrado"
        )
    return announcement

@announcements_router.patch("/{announcement_id}", response_model=schemas.AnnouncementResponse)
def update_announcement(
    announcement_id: int,
    announcement_update: schemas.AnnouncementUpdate,
    service: AnnouncementService = Depends(get_announcement_service),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    db_announcement = service.get_announcement(announcement_id)
    if not db_announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso não encontrado"
        )

    is_author = db_announcement.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar"
        )

    update_data = announcement_update.dict(exclude_unset=True)
    updated = service.update_announcement(announcement_id, update_data)
    return updated

@announcements_router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: int,
    service: AnnouncementService = Depends(get_announcement_service),
    current_user: models.User = Depends(require_roles(["teacher", "coordinator", "admin"]))
):
    db_announcement = service.get_announcement(announcement_id)
    if not db_announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso não encontrado"
        )

    is_author = db_announcement.authorId == current_user.id
    is_privileged = current_user.role in [models.UserRole.coordinator, models.UserRole.admin]

    if not is_author and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar"
        )

    success = service.delete_announcement(announcement_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao deletar aviso")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@announcements_router.get("/stats/count")
def get_announcements_count(
    service: AnnouncementService = Depends(get_announcement_service),
    current_user: models.User = Depends(get_current_active_user)
):
    total = service.repo.count()
    return {"total": total}


# --- 3. Incluir os roteadores no principal ---
# Rota raiz do publications que retorna os posts
@router.get("/", response_model=List[schemas.PostResponse])
def get_all_publications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: PostService = Depends(get_post_service),
):
    """Retorna todos os posts (comunicados) públicos"""
    return service.list_posts(skip=skip, limit=limit)

router.include_router(posts_router)
router.include_router(announcements_router)