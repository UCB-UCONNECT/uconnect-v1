# Scripts - UCONNECT API

Diretório contendo scripts utilitários para desenvolvimento e testes da API.

## Scripts Disponíveis

### 1. `run_server.py`
Inicia o servidor FastAPI com reload automático.

**Uso:**
```bash
# A partir da raiz do projeto
python scripts/run_server.py

# Ou diretamente
cd scripts && python run_server.py
```

**Detalhes:**
- Ativa o ambiente virtual automaticamente
- Servidor roda em `http://127.0.0.1:8000`
- Presione `CTRL+C` para parar
- Docs interativa em `/docs` e ReDoc em `/redoc`

---

### 2. `test_api_routes.py`
Script Python completo para testar todos os endpoints da API.

**Uso:**
```bash
# A partir da raiz do projeto
python scripts/test_api_routes.py

# Ou diretamente
cd scripts && python test_api_routes.py
```

**O que faz:**
- ✅ Inicia o servidor automaticamente
- ✅ Testa endpoints de saúde (`/health`, `/api/v1/health`)
- ✅ Testa endpoints públicos (events, groups, publications)
- ✅ Testa endpoints protegidos (retorna 401 sem token)
- ✅ Testa autenticação (login, validate)
- ✅ Para o servidor automaticamente
- ✅ Fornece relatório colorido com pass/fail/warning

**Requisitos:**
- Pacote `requests` instalado no venv

---

### 3. `test_phase1.sh`
Script Bash para testes rápidos usando curl.

**Uso:**
```bash
# Primeiro inicie o servidor em outro terminal
python scripts/run_server.py

# Então rode os testes em outro terminal
bash scripts/test_phase1.sh
```

**O que faz:**
- Testa endpoints de saúde
- Testa endpoints públicos
- Testa endpoints protegidos (verifica 401)
- Retorna resultados coloridos

---

## Fluxo Recomendado de Desenvolvimento

### Opção 1: Teste Rápido (Bash)
```bash
# Terminal 1: Inicia servidor
python scripts/run_server.py

# Terminal 2: Roda testes
bash scripts/test_phase1.sh
```

### Opção 2: Teste Automático (Python)
```bash
# Tudo automático em um comando
python scripts/test_api_routes.py
```

### Opção 3: Servidor Manual
```bash
# Apenas inicia o servidor
python scripts/run_server.py

# Acesse em outro terminal
curl http://127.0.0.1:8000/docs
```

---

## Notas

- Todos os scripts buscam automaticamente o diretório raiz do projeto
- O ambiente virtual (`pyenv`) é ativado automaticamente
- Scripts funcionam tanto executados a partir da raiz quanto do diretório `/scripts`
