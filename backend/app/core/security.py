# --------- SEGURANÇA E CRIPTOGRAFIA --------- #
"""
Este arquivo centraliza funções relacionadas à segurança de senhas.
Utiliza bcrypt via passlib para hash seguro de senhas.
"""
from passlib.context import CryptContext

# Contexto de segurança para bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_password(password: str) -> bytes:
    """Função interna para truncar a senha para o limite de 72 bytes do bcrypt."""
    return password.encode('utf-8')[:72]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto plano corresponde a um hash.
    Trunca a senha para compatibilidade com o bcrypt (máximo 72 bytes).
    """
    truncated_password = _truncate_password(plain_password)
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera o hash de uma senha usando bcrypt.
    Trunca a senha para compatibilidade (máximo 72 bytes).
    """
    truncated_password = _truncate_password(password)
    return pwd_context.hash(truncated_password)
