#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para iniciar o servidor com uvicorn --reload
Deve ser executado a partir do diretório raiz do projeto
"""

import subprocess
import sys
import os
from pathlib import Path

print("🚀 Iniciando servidor uvicorn com reload...\n")
print("=" * 60)
print("Comando: uvicorn backend.app.main:app --reload")
print("=" * 60)
print("\n✅ Servidor disponível em: http://127.0.0.1:8000")
print("📚 Docs interativa em: http://127.0.0.1:8000/docs")
print("📖 ReDoc em: http://127.0.0.1:8000/redoc")
print("\n⌨️  Pressione CTRL+C para parar o servidor\n")
print("=" * 60)

# Navegar para diretório raiz do projeto (pai do scripts/)
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# Ativar ambiente virtual e rodar uvicorn
try:
    subprocess.run(
        "source pyenv/bin/activate && uvicorn backend.app.main:app --reload",
        shell=True,
        executable="/bin/zsh"
    )
except KeyboardInterrupt:
    print("\n\n✅ Servidor parado com sucesso")
    sys.exit(0)
