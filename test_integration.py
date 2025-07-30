#!/usr/bin/env python3
"""
Script de teste de integração completa JusFiscal
Testa o fluxo completo: geração de conteúdo → leads → outreach
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

class JusFiscalTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """Registra resultado do teste"""
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if message:
            print(f"   {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_server_health(self):
        """Testa se o servidor está funcionando"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            success = response.status_code == 200
            self.log_test("Servidor Flask", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Servidor Flask", False, f"Erro: {str(e)}")
            return False
    
    def test_content_generation_flow(self):
        """Testa fluxo completo de geração de conteúdo"""
        print("\n📝 TESTANDO FLUXO DE GERAÇÃO DE CONTEÚDO")
        print("-" * 40)
        
        # 1. Listar templates disponíveis
        try:
            response = self.session.get(f"{self.base_url}/api/content/templates")
            templates = response.json() if response.status_code == 200 else []
            self.log_test("Listar Templates", response.status_code == 200, 
                         f"Encontrados {len(templates)} templates")
        except Exception as e:
            self.log_test("Listar Templates", False, str(e))
            return False
        
        # 2. Listar tópicos disponíveis
        try:
            response = self.session.get(f"{self.base_url}/api/content/topics")
            topics = response.json() if response.status_code == 200 else []
            self.log_test("Listar Tópicos", response.status_code == 200, 
                         f"Encontrados {len(topics)} tópicos")
        except Exception as e:
            self.log_test("Listar Tópicos", False, str(e))
            return False
        
        # 3. Gerar conteúdo para Instagram
        try:
            content_data = {
                "topic_id": 1,
                "template_type": "instagram",
                "target_sector": "Indústria"
            }
            response = self.session.post(f"{self.base_url}/api/content/generate", 
                                       json=content_data)
            success = response.status_code == 201
            self.log_test("Gerar Conteúdo Instagram", success, 
                         f"Status: {response.status_code}")
            
            if success:
                content = response.json()
                return content.get('id')
        except Exception as e:
            self.log_test("Gerar Conteúdo Instagram", False, str(e))
        
        return None
    
    def test_lead_management_flow(self):
        """Testa fluxo completo de gerenciamento de leads"""
        print("\n👥 TESTANDO FLUXO DE GERENCIAMENTO DE LEADS")
        print("-" * 40)
        
        # 1. Criar novo lead
        try:
            lead_data = {
                "company_name": "Empresa Teste Integração Ltda",
                "cnpj": "11.222.333/0001-44",
                "sector": "Tecnologia",
                "company_size": "Pequena",
                "contact_name": "Maria Teste",
                "email": "maria@testeintegracao.com.br",
                "phone": "(11) 88888-8888",
                "city": "São Paulo",
                "state": "SP"
            }
            response = self.session.post(f"{self.base_url}/api/leads", json=lead_data)
            success = response.status_code == 201
            self.log_test("Criar Lead", success, f"Status: {response.status_code}")
            
            if success:
                lead = response.json()
                lead_id = lead.get('id')
            else:
                return None
        except Exception as e:
            self.log_test("Criar Lead", False, str(e))
            return None
        
        # 2. Qualificar lead
        try:
            response = self.session.post(f"{self.base_url}/api/leads/{lead_id}/qualify")
            success = response.status_code == 200
            self.log_test("Qualificar Lead", success, f"Status: {response.status_code}")
            
            if success:
                qualified_lead = response.json()
                score = qualified_lead.get('score', 0)
                self.log_test("Score Calculado", score > 0, f"Score: {score}")
        except Exception as e:
            self.log_test("Qualificar Lead", False, str(e))
        
        # 3. Listar leads qualificados
        try:
            response = self.session.get(f"{self.base_url}/api/leads?status=qualified")
            success = response.status_code == 200
            if success:
                leads = response.json()
                qualified_count = len([l for l in leads if l.get('status') == 'qualified'])
                self.log_test("Listar Leads Qualificados", True, 
                             f"Encontrados {qualified_count} leads qualificados")
            else:
                self.log_test("Listar Leads Qualificados", False, 
                             f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Listar Leads Qualificados", False, str(e))
        
        return lead_id
    
    def test_outreach_campaign_flow(self, lead_id=None):
        """Testa fluxo completo de campanhas de outreach"""
        print("\n📧 TESTANDO FLUXO DE CAMPANHAS DE OUTREACH")
        print("-" * 40)
        
        # 1. Criar campanha de e-mail
        try:
            campaign_data = {
                "name": "Campanha Teste Integração",
                "type": "email",
                "target_sector": "Tecnologia",
                "min_score": 50,
                "template_id": 1
            }
            response = self.session.post(f"{self.base_url}/api/outreach/campaigns", 
                                       json=campaign_data)
            success = response.status_code == 201
            self.log_test("Criar Campanha", success, f"Status: {response.status_code}")
            
            if success:
                campaign = response.json()
                campaign_id = campaign.get('id')
            else:
                return None
        except Exception as e:
            self.log_test("Criar Campanha", False, str(e))
            return None
        
        # 2. Enviar mensagem para lead (se disponível)
        if lead_id:
            try:
                outreach_data = {
                    "lead_id": lead_id,
                    "campaign_id": campaign_id,
                    "channel": "email",
                    "template_id": 1
                }
                response = self.session.post(f"{self.base_url}/api/outreach/send", 
                                           json=outreach_data)
                success = response.status_code == 201
                self.log_test("Enviar Outreach", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Enviar Outreach", False, str(e))
        
        # 3. Listar interações
        try:
            response = self.session.get(f"{self.base_url}/api/outreach/interactions")
            success = response.status_code == 200
            if success:
                interactions = response.json()
                self.log_test("Listar Interações", True, 
                             f"Encontradas {len(interactions)} interações")
            else:
                self.log_test("Listar Interações", False, 
                             f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Listar Interações", False, str(e))
        
        return campaign_id
    
    def test_publication_flow(self, content_id=None):
        """Testa fluxo de publicação"""
        print("\n📱 TESTANDO FLUXO DE PUBLICAÇÃO")
        print("-" * 40)
        
        if not content_id:
            self.log_test("Publicação", False, "Nenhum conteúdo disponível")
            return
        
        # 1. Agendar publicação
        try:
            publication_data = {
                "content_id": content_id,
                "platform": "instagram",
                "scheduled_for": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            response = self.session.post(f"{self.base_url}/api/publications/schedule", 
                                       json=publication_data)
            success = response.status_code == 201
            self.log_test("Agendar Publicação", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Agendar Publicação", False, str(e))
        
        # 2. Listar publicações agendadas
        try:
            response = self.session.get(f"{self.base_url}/api/publications")
            success = response.status_code == 200
            if success:
                publications = response.json()
                scheduled_count = len([p for p in publications if p.get('status') == 'scheduled'])
                self.log_test("Listar Publicações", True, 
                             f"Encontradas {scheduled_count} publicações agendadas")
            else:
                self.log_test("Listar Publicações", False, 
                             f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Listar Publicações", False, str(e))
    
    def test_scheduler_control(self):
        """Testa controle do agendador"""
        print("\n⏰ TESTANDO CONTROLE DO AGENDADOR")
        print("-" * 40)
        
        # 1. Verificar status
        try:
            response = self.session.get(f"{self.base_url}/api/scheduler/status")
            success = response.status_code == 200
            if success:
                status = response.json()
                self.log_test("Status do Agendador", True, 
                             f"Status: {status.get('status', 'unknown')}")
            else:
                self.log_test("Status do Agendador", False, 
                             f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Status do Agendador", False, str(e))
        
        # 2. Iniciar agendador
        try:
            response = self.session.post(f"{self.base_url}/api/scheduler/start")
            success = response.status_code == 200
            self.log_test("Iniciar Agendador", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Iniciar Agendador", False, str(e))
    
    def run_integration_tests(self):
        """Executa todos os testes de integração"""
        print("🚀 INICIANDO TESTES DE INTEGRAÇÃO JUSFISCAL")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        # Verificar servidor
        if not self.test_server_health():
            print("\n❌ Servidor não está funcionando. Abortando testes.")
            return
        
        # Executar testes de fluxo
        content_id = self.test_content_generation_flow()
        lead_id = self.test_lead_management_flow()
        campaign_id = self.test_outreach_campaign_flow(lead_id)
        self.test_publication_flow(content_id)
        self.test_scheduler_control()
        
        # Resumo dos resultados
        self.print_test_summary()
    
    def print_test_summary(self):
        """Imprime resumo dos testes"""
        print("\n📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de testes: {total_tests}")
        print(f"✅ Passou: {passed_tests}")
        print(f"❌ Falhou: {failed_tests}")
        print(f"📈 Taxa de sucesso: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for test in self.test_results:
                if not test['success']:
                    print(f"   - {test['test']}: {test['message']}")
        
        print("\n🏁 TESTES DE INTEGRAÇÃO CONCLUÍDOS")
        print("=" * 60)

if __name__ == "__main__":
    tester = JusFiscalTester()
    tester.run_integration_tests()

