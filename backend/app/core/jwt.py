# --------- JWT TOKEN HANDLING --------- #
"""
Este arquivo centraliza funções relacionadas a JWT.
Responsável por decodificar, validar e criar tokens JWT.
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .config import settings


def decode_token(token: str) -> dict | None:
    """
    Decodifica um token JWT e retorna o payload.
    Retorna None se o token for inválido.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_access_token(data: dict, expires_minutes: int = None) -> tuple[str, datetime]:
    """
    Cria um novo token de acesso JWT.
    Retorna uma tupla (token, data_expiracao).
    """
    to_encode = data.copy()
    if expires_minutes:
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "sub": data.get("sub")})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, expire
