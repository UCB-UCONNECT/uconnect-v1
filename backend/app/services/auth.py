from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .user import UserService
from ..core.jwt import create_access_token
from .. import models


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def login(self, registration: str, password: str) -> Dict[str, Any]:
        user = self.user_service.authenticate_user(registration, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Matrícula ou senha incorretas")

        if user.accessStatus != models.AccessStatus.active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso inativo")

        # O token deve carregar o ID do usuário em 'sub' para compatibilidade com get_current_user
        token, expire = create_access_token(data={"sub": str(user.id)})
        db_session = models.Session(token=token, userId=user.id, startDate=datetime.utcnow(), expirationDate=expire)
        self.db.add(db_session)
        self.db.commit()
        return {"access_token": token, "token_type": "bearer", "expires_at": expire}

    def logout(self, token: str) -> bool:
        session = self.db.query(models.Session).filter(models.Session.token == token).first()
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False

    def validate(self, token: str) -> Dict[str, Any]:
        session = self.db.query(models.Session).filter(models.Session.token == token).first()
        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida")

        if session.expirationDate < datetime.utcnow():
            self.db.delete(session)
            self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão expirada")

        return {"valid": True, "expires_at": session.expirationDate}
