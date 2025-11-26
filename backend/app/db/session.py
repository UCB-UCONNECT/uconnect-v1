# --------- DATABASE SESSION --------- #
"""
Este arquivo configura a sessão de banco de dados com SQLAlchemy.
Inclui engine, pool de conexões e função de dependência para FastAPI.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Lê a URL do banco de dados a partir das variáveis de ambiente
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://avnadmin:AVNS_ZNdJaYqcEhNaEf1dsCl@uconnect-uconnect.c.aivencloud.com:24757/defaultdb"
)

# Converte a variável de ambiente para booleano
ECHO_SQL = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "t")

# Engine com pool otimizado para produção
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=ECHO_SQL,
)

# Factory para criar novas sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db():
    """
    Dependência FastAPI para injetar sessão de BD.
    Garante fechamento seguro da sessão ao final da requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
