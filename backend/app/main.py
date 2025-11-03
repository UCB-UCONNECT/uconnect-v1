# ---------------- ARQUIVO PRINCIPAL DA APLICAÇÃO  ---------------- #
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from .routers import auth, users, events, groups, publications, chat
from .db import Base, engine

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Instanciar FastAPI
app = FastAPI(
    title="UCONNECT API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# OTIMIZAÇÃO 1: Adicionar compressão GZIP
app.add_middleware(GZipMiddleware, minimum_size=1000)

# OTIMIZAÇÃO 2: CORS configurado
origins = {
    "null",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # OTIMIZAÇÃO: Cache de preflight requests
    max_age=3600,
)

# Incluir rotas
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(groups.router)
app.include_router(publications.router)
app.include_router(chat.router)

# Rotas básicas
@app.get("/")
def root():
    return {
        "message": "UCONNECT API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
    