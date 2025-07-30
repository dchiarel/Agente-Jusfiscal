#!/usr/bin/env python3
"""
Script de teste para as APIs do backend JusFiscal
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_api_endpoint(method, endpoint, data=None, expected_status=200):
    """Testa um endpoint da API"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"[{method}] {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ PASSOU")
            if response.content:
                try:
                    result = response.json()
                    print(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
                except:
                    print(f"Resposta: {response.text}")
        else:
            print(f"❌ FALHOU - Esperado: {expected_status}, Recebido: {response.status_code}")
            print(f"Erro: {response.text}")
        
        print("-" * 50)
        return response.status_code == expected_status
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO DE CONEXÃO - Servidor não está rodando em {BASE_URL}")
        print("-" * 50)
        return False
    except Exception as e:
        print(f"❌ ERRO - {str(e)}")
        print("-" * 50)
        return False

def test_content_apis():
    """Testa APIs de conteúdo"""
    print("🧪 TESTANDO APIs DE CONTEÚDO")
    print("=" * 50)
    
    # Listar conteúdos
    test_api_endpoint("GET", "/api/content")
    
    # Gerar conteúdo
    content_data = {
        "topic_id": 1,
        "template_type": "instagram",
        "target_sector": "Indústria"
    }
    test_api_endpoint("POST", "/api/content/generate", content_data)
    
    # Listar templates
    test_api_endpoint("GET", "/api/content/templates")
    
    # Listar tópicos
    test_api_endpoint("GET", "/api/content/topics")

def test_lead_apis():
    """Testa APIs de leads"""
    print("🧪 TESTANDO APIs DE LEADS")
    print("=" * 50)
    
    # Listar leads
    test_api_endpoint("GET", "/api/leads")
    
    # Criar lead
    lead_data = {
        "company_name": "Empresa Teste Ltda",
        "cnpj": "12.345.678/0001-99",
        "sector": "Tecnologia",
        "contact_name": "João Teste",
        "email": "joao@teste.com.br",
        "phone": "(11) 99999-9999"
    }
    test_api_endpoint("POST", "/api/leads", lead_data)
    
    # Qualificar lead
    test_api_endpoint("POST", "/api/leads/1/qualify")

def test_outreach_apis():
    """Testa APIs de outreach"""
    print("🧪 TESTANDO APIs DE OUTREACH")
    print("=" * 50)
    
    # Listar campanhas
    test_api_endpoint("GET", "/api/outreach/campaigns")
    
    # Criar campanha
    campaign_data = {
        "name": "Campanha Teste",
        "type": "email",
        "target_sector": "Tecnologia",
        "min_score": 60
    }
    test_api_endpoint("POST", "/api/outreach/campaigns", campaign_data)
    
    # Listar interações
    test_api_endpoint("GET", "/api/outreach/interactions")

def test_publication_apis():
    """Testa APIs de publicação"""
    print("🧪 TESTANDO APIs DE PUBLICAÇÃO")
    print("=" * 50)
    
    # Listar publicações
    test_api_endpoint("GET", "/api/publications")
    
    # Agendar publicação
    publication_data = {
        "content_id": 1,
        "platform": "instagram",
        "scheduled_for": "2024-01-20T10:00:00"
    }
    test_api_endpoint("POST", "/api/publications/schedule", publication_data)

def test_scheduler_apis():
    """Testa APIs do agendador"""
    print("🧪 TESTANDO APIs DO AGENDADOR")
    print("=" * 50)
    
    # Status do agendador
    test_api_endpoint("GET", "/api/scheduler/status")
    
    # Iniciar agendador
    test_api_endpoint("POST", "/api/scheduler/start")
    
    # Pausar agendador
    test_api_endpoint("POST", "/api/scheduler/pause")

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO BACKEND JUSFISCAL")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor Flask está rodando")
        else:
            print("❌ Servidor Flask não está respondendo corretamente")
            return
    except:
        print("❌ Servidor Flask não está rodando")
        print("💡 Execute: cd tax_content_agent && source venv/bin/activate && python src/main.py")
        return
    
    print()
    
    # Executar testes
    test_content_apis()
    test_lead_apis()
    test_outreach_apis()
    test_publication_apis()
    test_scheduler_apis()
    
    print("🏁 TESTES CONCLUÍDOS")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()

