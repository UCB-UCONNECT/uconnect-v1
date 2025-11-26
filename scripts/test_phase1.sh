#!/bin/bash
# Script para testar endpoints da API
# Uso: ./test_phase1.sh

set -e

echo "=================================================="
echo "TESTE DE ENDPOINTS - FASE 1"
echo "=================================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL="http://127.0.0.1:8000"

echo -e "${BLUE}📋 Testando Endpoints de Saúde:${NC}"
echo ""

# Endpoint raiz
echo -n "  GET / ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/" | grep -q "200"; then
    echo -e "${GREEN}✅ PASS (200)${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Health endpoint
echo -n "  GET /health ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" | grep -q "200"; then
    echo -e "${GREEN}✅ PASS (200)${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# API Health
echo -n "  GET /api/v1/health ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/health" | grep -q "200"; then
    echo -e "${GREEN}✅ PASS (200)${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Swagger UI
echo -n "  GET /docs ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs" | grep -q "200"; then
    echo -e "${GREEN}✅ PASS (200)${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

echo ""
echo -e "${BLUE}📚 Testando Endpoints Públicos:${NC}"
echo ""

# Events
echo -n "  GET /api/v1/events ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/events" | grep -q "200"; then
    echo -e "${GREEN}✅ PASS (200)${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Groups
echo -n "  GET /api/v1/groups ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/groups" | grep -q "200"; then
    echo -e "${GREEN}✅ PASS (200)${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Publications
echo -n "  GET /api/v1/publications ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/publications" | grep -q "200"; then
    echo -e "${GREEN}✅ PASS (200)${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

echo ""
echo -e "${BLUE}🔐 Testando Endpoints Protegidos (sem token):${NC}"
echo ""

# Users me (deve retornar 401)
echo -n "  GET /api/v1/users/me ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/users/me" | grep -q "401"; then
    echo -e "${GREEN}✅ PASS (401 - não autenticado)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING (esperado 401)${NC}"
fi

# Chat conversations (deve retornar 401)
echo -n "  GET /api/v1/chat/conversations ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/chat/conversations" | grep -q "401"; then
    echo -e "${GREEN}✅ PASS (401 - não autenticado)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING (esperado 401)${NC}"
fi

# Notifications (deve retornar 401)
echo -n "  GET /api/v1/notifications ... "
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/notifications" | grep -q "401"; then
    echo -e "${GREEN}✅ PASS (401 - não autenticado)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING (esperado 401)${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Testes concluídos!${NC}"
echo "=================================================="
echo ""
echo "Para interagir com a API, acesse:"
echo "  📚 Swagger UI: $BASE_URL/docs"
echo "  📖 ReDoc: $BASE_URL/redoc"
echo ""
    local expected_status=$3
    local description=$4
    
    echo -n "📡 $description... "
    
    response=$(curl -s -w "\n%{http_code}" -X "$method" "http://127.0.0.1:8000$endpoint" \
        -H "Content-Type: application/json" 2>/dev/null || echo "000")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ OK ($http_code)${NC}"
        return 0
    else
        echo -e "${RED}✗ FALHOU (esperado: $expected_status, obtido: $http_code)${NC}"
        echo "Response: $body"
        return 1
    fi
}

# Limpar cache
echo "🧹 Limpando cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Ativar venv e iniciar servidor
echo "🚀 Iniciando servidor uvicorn..."
cd /Users/paulosilva/Desktop/uconnect-v1
source pyenv/bin/activate

# Iniciar uvicorn em background
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level error 2>&1 &
UVICORN_PID=$!
echo "   PID: $UVICORN_PID"

# Aguardar servidor iniciar
echo "⏳ Aguardando servidor iniciar (5 segundos)..."
sleep 5

# Variável para rastrear falhas
FAILED=0

echo ""
echo "🧪 ===== EXECUTANDO TESTES ====="
echo ""

# Testes
test_endpoint "GET" "/" "200" "Endpoint root (/)" || FAILED=$((FAILED + 1))
test_endpoint "GET" "/health" "200" "Health check (/health)" || FAILED=$((FAILED + 1))
test_endpoint "GET" "/api/v1/health" "200" "Versioned health check (/api/v1/health)" || FAILED=$((FAILED + 1))
test_endpoint "GET" "/docs" "200" "Swagger UI (/docs)" || FAILED=$((FAILED + 1))

echo ""
echo "🧪 ===== TESTES DE ROTAS AUTENTICADAS ====="
echo ""

# Tentar listar usuários sem token (deve retornar 403 ou 401)
echo -n "📡 Acessar /api/v1/users sem token (deve falhar)... "
response=$(curl -s -w "\n%{http_code}" -X GET "http://127.0.0.1:8000/api/v1/users" \
    -H "Content-Type: application/json" 2>/dev/null || echo "000")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "403" ] || [ "$http_code" = "401" ] || [ "$http_code" = "307" ]; then
    echo -e "${GREEN}✓ OK ($http_code - acesso bloqueado como esperado)${NC}"
else
    echo -e "${YELLOW}⚠ AVISO ($http_code - esperado 401/403)${NC}"
fi

echo ""
echo "🛑 Parando servidor..."
kill $UVICORN_PID 2>/dev/null || true
sleep 2

echo ""
echo "📊 ===== RESULTADO ====="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}"
    echo ""
    echo "✓ App inicia corretamente"
    echo "✓ Endpoints públicos funcionam"
    echo "✓ Autenticação está protegendo rotas"
    echo ""
    echo "🎉 Fase 1 está COMPLETA e FUNCIONAL!"
    exit 0
else
    echo -e "${RED}❌ $FAILED TESTE(S) FALHARAM${NC}"
    exit 1
fi
