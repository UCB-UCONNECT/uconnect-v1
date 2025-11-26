#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Teste - Fase 1
Testa todos os endpoints da API após reorganização de infraestrutura
Deve ser executado a partir do diretório raiz do projeto
"""

import subprocess
import time
import requests
import signal
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

# Cores para terminal
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

class APITester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.server_process = None
        self.results = {"passed": 0, "failed": 0, "warnings": 0}
        self.token = None
        
    def start_server(self):
        """Inicia o servidor uvicorn"""
        print(f"{BLUE}🚀 Iniciando servidor uvicorn com reload...{NC}")
        try:
            # Navegar para diretório raiz do projeto (pai do scripts/)
            project_root = Path(__file__).parent.parent
            os.chdir(project_root)
            
            # Iniciar servidor
            cmd = "source pyenv/bin/activate && uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
            self.server_process = subprocess.Popen(
                cmd,
                shell=True,
                executable="/bin/zsh",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Aguardar servidor iniciar
            print(f"{YELLOW}⏳ Aguardando servidor iniciar (aguardando 8 segundos)...{NC}")
            time.sleep(8)
            
            # Testar conexão
            for i in range(5):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"{GREEN}✅ Servidor iniciado com sucesso!{NC}\n")
                        return True
                except:
                    if i < 4:
                        time.sleep(1)
            
            print(f"{RED}❌ Falha ao conectar no servidor após 5 tentativas{NC}")
            return False
            
        except Exception as e:
            print(f"{RED}❌ Erro ao iniciar servidor: {e}{NC}")
            return False
    
    def stop_server(self):
        """Para o servidor uvicorn"""
        if self.server_process:
            print(f"\n{BLUE}🛑 Parando servidor...{NC}")
            try:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                time.sleep(2)
            except:
                pass
    
    def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                     data: dict = None, headers: dict = None) -> Tuple[bool, str]:
        """Testa um endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=5)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=5)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=5)
            else:
                return False, f"Método {method} não suportado"
            
            if response.status_code == expected_status:
                return True, f"{method} {endpoint} -> {response.status_code}"
            else:
                return False, f"{method} {endpoint} -> {response.status_code} (esperado {expected_status})"
        except requests.exceptions.Timeout:
            return False, f"{method} {endpoint} -> TIMEOUT"
        except Exception as e:
            return False, f"{method} {endpoint} -> ERRO: {str(e)}"
    
    def run_tests(self):
        """Executa todos os testes"""
        print(f"{CYAN}{'='*70}{NC}")
        print(f"{CYAN}TESTE DE ENDPOINTS - FASE 1{NC}")
        print(f"{CYAN}{'='*70}{NC}\n")
        
        # Testes de saúde
        print(f"{BLUE}📋 Testando Endpoints de Saúde:{NC}")
        tests = [
            ("GET", "/", 200),
            ("GET", "/health", 200),
            ("GET", "/api/v1/health", 200),
            ("GET", "/docs", 200),
            ("GET", "/redoc", 200),
        ]
        
        for method, endpoint, expected in tests:
            passed, msg = self.test_endpoint(method, endpoint, expected)
            status = f"{GREEN}✅ PASS{NC}" if passed else f"{RED}❌ FAIL{NC}"
            print(f"  {status} - {msg}")
            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        # Testes de autenticação (públicos)
        print(f"\n{BLUE}🔐 Testando Endpoints de Autenticação:{NC}")
        tests_auth = [
            ("GET", "/api/v1/auth/validate", 401),  # Sem token deve retornar 401
            ("POST", "/api/v1/auth/login", 422),     # Sem dados deve retornar 422 (validação)
        ]
        
        for method, endpoint, expected in tests_auth:
            passed, msg = self.test_endpoint(method, endpoint, expected)
            status = f"{GREEN}✅ PASS{NC}" if passed else f"{RED}❌ FAIL{NC}"
            print(f"  {status} - {msg}")
            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        # Testes de rotas públicas (sem autenticação)
        print(f"\n{BLUE}📚 Testando Endpoints Públicos:{NC}")
        tests_public = [
            ("GET", "/api/v1/events", 200),
            ("GET", "/api/v1/groups", 200),
            ("GET", "/api/v1/publications", 200),
        ]
        
        for method, endpoint, expected in tests_public:
            passed, msg = self.test_endpoint(method, endpoint, expected)
            status = f"{GREEN}✅ PASS{NC}" if passed else f"{RED}❌ FAIL{NC}"
            print(f"  {status} - {msg}")
            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        # Testes de rotas protegidas (esperado 401/403 sem token)
        print(f"\n{BLUE}🔒 Testando Endpoints Protegidos (sem token):{NC}")
        tests_protected = [
            ("GET", "/api/v1/users/me", 401),
            ("GET", "/api/v1/chat/conversations", 401),
            ("GET", "/api/v1/notifications", 401),
            ("GET", "/api/v1/access", 401),
        ]
        
        for method, endpoint, expected in tests_protected:
            passed, msg = self.test_endpoint(method, endpoint, expected)
            status = f"{GREEN}✅ PASS{NC}" if passed else f"{RED}❌ FAIL{NC}"
            print(f"  {status} - {msg}")
            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        # Resumo final
        print(f"\n{CYAN}{'='*70}{NC}")
        print(f"{CYAN}RESUMO DOS TESTES{NC}")
        print(f"{CYAN}{'='*70}{NC}")
        total = self.results["passed"] + self.results["failed"] + self.results["warnings"]
        print(f"{GREEN}✅ Passou: {self.results['passed']}{NC}")
        print(f"{RED}❌ Falhou: {self.results['failed']}{NC}")
        print(f"{YELLOW}⚠️  Avisos: {self.results['warnings']}{NC}")
        print(f"{CYAN}Total: {total} testes{NC}")
        print(f"{CYAN}{'='*70}{NC}\n")
        
        if self.results["failed"] == 0:
            print(f"{GREEN}🎉 TODOS OS TESTES PASSARAM! Fase 1 validada com sucesso!{NC}\n")
            return 0
        else:
            print(f"{RED}⚠️  Alguns testes falharam. Verifique os detalhes acima.{NC}\n")
            return 1

def main():
    tester = APITester()
    
    # Tratamento de sinais
    def signal_handler(sig, frame):
        tester.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Iniciar servidor
    if not tester.start_server():
        print(f"{RED}Não foi possível iniciar o servidor. Saindo...{NC}")
        tester.stop_server()
        sys.exit(1)
    
    try:
        # Executar testes
        exit_code = tester.run_tests()
    finally:
        # Parar servidor
        tester.stop_server()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
