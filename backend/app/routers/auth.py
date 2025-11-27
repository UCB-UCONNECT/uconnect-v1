# ---------------- ROTAS DE AUTENTICAÇÃO ---------------- #
"""
Este arquivo (routers/auth.py) define os endpoints da API relacionados à
autenticação de usuários. Ele gerencia o ciclo de vida da sessão de um
usuário.

Suas responsabilidades incluem:
- Definir o endpoint `/login` para validar credenciais (matrícula e senha).
- Criar e armazenar sessões no banco de dados, gerando um token JWT.
- Definir o endpoint `/logout` para invalidar um token e encerrar a sessão.
- Fornecer um endpoint `/validate` para que o frontend possa verificar se uma
  sessão ainda é ativa.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from ..db.session import get_db
from ..dependencies import oauth2_scheme
from .. import models, schemas
from ..services import AuthService

# --- Configuração do Roteador e Modelos de Dados ---
# O `APIRouter` agrupa as rotas de autenticação sob o prefixo `/auth`.
# Os modelos Pydantic (`LoginRequest`, `TokenResponse`) garantem que os dados
# enviados e recebidos nas requisições tenham a estrutura correta.
router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    registration: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime

# --- Endpoint: Login de Usuário ---
# Esta rota recebe a matrícula e a senha, valida as credenciais contra o banco
# de dados, verifica se o usuário está ativo e, em caso de sucesso, cria um
# novo token JWT e registra a sessão no banco antes de retorná-la ao cliente.
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    # Remove espaços em branco da matrícula e da senha.
    user_registration = login_data.registration.strip()
    user_password = login_data.password.strip()

    return auth_service.login(user_registration, user_password)


# --- Endpoint: Logout de Usuário ---
# Invalida a sessão do usuário. A rota recebe um token JWT, localiza a
# sessão correspondente no banco de dados e a remove, efetivamente
# desconectando o usuário.
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)):
    auth_service.logout(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Endpoint: Validação de Sessão ---
# Permite verificar a validade de um token. A rota checa se a sessão
# associada ao token existe e se não expirou. Retorna um status de sucesso
# ou um erro de não autorizado.
@router.get("/validate")
def validate_session(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.validate(token)
