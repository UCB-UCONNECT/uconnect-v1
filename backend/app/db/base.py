# --------- DATABASE BASE --------- #
"""
Este arquivo define a Base declarativa para os modelos ORM.
Todos os modelos de tabela devem herdar desta classe.
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
