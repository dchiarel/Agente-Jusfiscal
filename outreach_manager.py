import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.models.lead import db, Lead, LeadInteraction
from src.models.content import ContentTemplate
from src.services.lead_manager import LeadManager

class OutreachManager:
    """Gerencia contato inicial e follow-up com leads"""
    
    def __init__(self):
        self.lead_manager = LeadManager()
    
    def send_initial_email(self, lead_id: int, template_type: str = 'email') -> Dict:
        """
        Envia e-mail inicial para um lead
        
        Args:
            lead_id: ID do lead
            template_type: Tipo de template a usar
        
        Returns:
            Dict com resultado do envio
        """
        
        try:
            lead = Lead.query.get(lead_id)
            if not lead:
                return {'success': False, 'error': 'Lead não encontrado'}
            
            if not lead.email:
                return {'success': False, 'error': 'Lead não possui e-mail'}
            
            # Busca template de e-mail
            template = ContentTemplate.query.filter_by(content_type=template_type).first()
            if not template:
                return {'success': False, 'error': 'Template não encontrado'}
            
            # Personaliza e-mail para o lead
            email_content = self._personalize_email_template(template, lead)
            
            # Envia e-mail (simulado - integrar com serviço real)
            result = self._send_email(
                to_email=lead.email,
                subject=email_content['subject'],
                content=email_content['content'],
                lead_id=lead_id
            )
            
            if result['success']:
                # Registra interação
                self.lead_manager.record_interaction(lead_id, {
                    'interaction_type': 'email',
                    'channel': 'email_marketing',
                    'subject': email_content['subject'],
                    'message': email_content['content'],
                    'status': 'sent',
                    'metadata': {
                        'template_used': template.name,
                        'personalization_data': email_content.get('personalization_data', {})
                    }
                })
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_linkedin_message(self, lead_id: int, message_type: str = 'initial') -> Dict:
        """
        Envia mensagem inicial no LinkedIn
        
        Args:
            lead_id: ID do lead
            message_type: Tipo de mensagem (initial, follow_up)
        
        Returns:
            Dict com resultado do envio
        """
        
        try:
            lead = Lead.query.get(lead_id)
            if not lead:
                return {'success': False, 'error': 'Lead não encontrado'}
            
            if not lead.linkedin_profile:
                return {'success': False, 'error': 'Lead não possui perfil LinkedIn'}
            
            # Gera mensagem personalizada
            message_content = self._generate_linkedin_message(lead, message_type)
            
            # Envia mensagem (simulado - integrar com API do LinkedIn)
            result = self._send_linkedin_message(
                profile_url=lead.linkedin_profile,
                message=message_content['message'],
                lead_id=lead_id
            )
            
            if result['success']:
                # Registra interação
                self.lead_manager.record_interaction(lead_id, {
                    'interaction_type': 'linkedin',
                    'channel': 'linkedin_dm',
                    'subject': f'Mensagem LinkedIn - {message_type}',
                    'message': message_content['message'],
                    'status': 'sent',
                    'metadata': {
                        'message_type': message_type,
                        'profile_url': lead.linkedin_profile
                    }
                })
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_instagram_dm(self, lead_id: int, message_type: str = 'initial') -> Dict:
        """
        Envia mensagem direta no Instagram
        
        Args:
            lead_id: ID do lead
            message_type: Tipo de mensagem
        
        Returns:
            Dict com resultado do envio
        """
        
        try:
            lead = Lead.query.get(lead_id)
            if not lead:
                return {'success': False, 'error': 'Lead não encontrado'}
            
            if not lead.instagram_profile:
                return {'success': False, 'error': 'Lead não possui perfil Instagram'}
            
            # Gera mensagem personalizada para Instagram
            message_content = self._generate_instagram_message(lead, message_type)
            
            # Envia DM (simulado - integrar com API do Instagram)
            result = self._send_instagram_dm(
                profile_url=lead.instagram_profile,
                message=message_content['message'],
                lead_id=lead_id
            )
            
            if result['success']:
                # Registra interação
                self.lead_manager.record_interaction(lead_id, {
                    'interaction_type': 'instagram',
                    'channel': 'instagram_dm',
                    'subject': f'DM Instagram - {message_type}',
                    'message': message_content['message'],
                    'status': 'sent',
                    'metadata': {
                        'message_type': message_type,
                        'profile_url': lead.instagram_profile
                    }
                })
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _personalize_email_template(self, template: ContentTemplate, lead: Lead) -> Dict:
        """Personaliza template de e-mail para o lead específico"""
        
        # Dados de personalização
        personalization_data = {
            'nome_contato': lead.contact_name or 'Responsável',
            'nome_empresa': lead.company_name,
            'setor': lead.sector or 'seu setor',
            'assunto': f'Oportunidade de Recuperação Tributária para {lead.company_name}',
            'introducao_personalizada': self._generate_intro_for_sector(lead.sector, lead.company_size),
            'oportunidade_1': self._get_opportunity_for_sector(lead.sector, 1),
            'oportunidade_2': self._get_opportunity_for_sector(lead.sector, 2),
            'oportunidade_3': self._get_opportunity_for_sector(lead.sector, 3),
            'proposta_valor': self._generate_value_proposition(lead),
            'call_to_action': 'Que tal agendar uma conversa de 15 minutos para apresentar as oportunidades específicas para sua empresa?',
            'nome_consultor': 'Equipe JusFiscal',
            'empresa': 'JusFiscal',
            'contato': 'WhatsApp: (11) 99999-9999 | E-mail: contato@jusfiscal.com.br'
        }
        
        # Substitui variáveis no template
        content = template.template_content
        for key, value in personalization_data.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        return {
            'subject': personalization_data['assunto'],
            'content': content,
            'personalization_data': personalization_data
        }
    
    def _generate_intro_for_sector(self, sector: str, company_size: str) -> str:
        """Gera introdução personalizada por setor"""
        
        intros = {
            'Indústria': f'Sabemos que {company_size.lower() if company_size else "pequenas e médias"} indústrias frequentemente têm oportunidades significativas de recuperação de créditos tributários.',
            'Comércio': f'Empresas do comércio, especialmente {company_size.lower() if company_size else "PMEs"}, costumam ter excelentes oportunidades de recuperação tributária.',
            'Serviços': f'Prestadores de serviços como sua empresa frequentemente podem recuperar valores significativos em tributos.',
            'Construção': f'O setor de construção possui particularidades tributárias que geram boas oportunidades de recuperação.',
            'Tecnologia': f'Empresas de tecnologia têm características específicas que podem gerar créditos tributários interessantes.'
        }
        
        return intros.get(sector, 'Sua empresa pode ter oportunidades interessantes de recuperação de créditos tributários.')
    
    def _get_opportunity_for_sector(self, sector: str, position: int) -> str:
        """Retorna oportunidades específicas por setor"""
        
        opportunities = {
            'Indústria': [
                'Créditos de PIS/COFINS sobre insumos do processo produtivo',
                'Recuperação de ICMS na base de cálculo do PIS/COFINS',
                'Créditos de IPI sobre matérias-primas'
            ],
            'Comércio': [
                'ICMS na base de cálculo do PIS/COFINS',
                'Créditos de PIS/COFINS sobre mercadorias para revenda',
                'INSS sobre verbas indenizatórias'
            ],
            'Serviços': [
                'INSS sobre verbas indenizatórias (férias, 13º, aviso prévio)',
                'PIS/COFINS sobre receitas não operacionais',
                'Revisão de base de cálculo de tributos'
            ]
        }
        
        sector_opportunities = opportunities.get(sector, [
            'Revisão de tributos dos últimos 5 anos',
            'Análise de base de cálculo de impostos',
            'Verificação de recolhimentos indevidos'
        ])
        
        if position <= len(sector_opportunities):
            return sector_opportunities[position - 1]
        else:
            return 'Outras oportunidades específicas para seu segmento'
    
    def _generate_value_proposition(self, lead: Lead) -> str:
        """Gera proposta de valor personalizada"""
        
        if lead.company_size == 'Micro':
            return 'Mesmo micro empresas podem recuperar valores entre R$ 10.000 e R$ 100.000, que fazem toda diferença no fluxo de caixa.'
        elif lead.company_size == 'Pequena':
            return 'Pequenas empresas como a sua frequentemente recuperam entre R$ 50.000 e R$ 300.000 em créditos tributários.'
        elif lead.company_size == 'Média':
            return 'Médias empresas costumam ter potencial de recuperação entre R$ 200.000 e R$ 1.000.000 ou mais.'
        else:
            return 'PMEs do seu setor frequentemente recuperam valores significativos que impactam positivamente o fluxo de caixa.'
    
    def _generate_linkedin_message(self, lead: Lead, message_type: str) -> Dict:
        """Gera mensagem personalizada para LinkedIn"""
        
        if message_type == 'initial':
            message = f"""Olá {lead.contact_name or 'pessoal da ' + lead.company_name}!

Vi que vocês atuam no setor {lead.sector or 'empresarial'} e gostaria de compartilhar uma informação que pode ser valiosa para a {lead.company_name}.

Muitas PMEs deixam de recuperar milhares de reais em impostos pagos a maior nos últimos 5 anos. Especializamos em identificar essas oportunidades de forma gratuita e sem compromisso.

Que tal uma conversa rápida para apresentar como isso funciona?

Abraços,
Equipe JusFiscal"""
        
        elif message_type == 'follow_up':
            message = f"""Olá novamente!

Espero que esteja tudo bem com vocês na {lead.company_name}.

Queria retomar nossa conversa sobre recuperação de créditos tributários. Sei que o dia a dia é corrido, mas essa pode ser uma oportunidade importante para melhorar o fluxo de caixa da empresa.

Posso enviar um material rápido sobre as principais oportunidades para empresas do setor {lead.sector or 'de vocês'}?

Abraços,
Equipe JusFiscal"""
        
        else:
            message = f"""Olá {lead.contact_name or 'pessoal da ' + lead.company_name}!

Obrigado pelo interesse em nossos serviços de recuperação tributária.

Vou preparar uma análise preliminar específica para a {lead.company_name} e entro em contato em breve com mais detalhes.

Abraços,
Equipe JusFiscal"""
        
        return {'message': message}
    
    def _generate_instagram_message(self, lead: Lead, message_type: str) -> Dict:
        """Gera mensagem personalizada para Instagram"""
        
        if message_type == 'initial':
            message = f"""Oi! 👋

Vi o perfil da {lead.company_name} e achei super interessante o trabalho de vocês! 

Trabalho com recuperação de créditos tributários e muitas empresas como a de vocês conseguem recuperar valores significativos em impostos pagos a maior.

Que tal trocar uma ideia sobre isso? Posso mandar algumas dicas por aqui mesmo! 😊

#PME #RecuperacaoTributaria #JusFiscal"""
        
        elif message_type == 'follow_up':
            message = f"""Oi pessoal! 

Espero que estejam bem! 😊

Queria retomar nossa conversa sobre recuperação tributária. Preparei um material bem legal com dicas específicas para empresas como a {lead.company_name}.

Posso compartilhar com vocês?

#DicasTributarias #PME #JusFiscal"""
        
        else:
            message = f"""Oi!

Obrigado pelo interesse! 🙏

Vou preparar uma análise específica para vocês e mando mais detalhes em breve.

Qualquer dúvida, é só chamar!

#JusFiscal #RecuperacaoTributaria"""
        
        return {'message': message}
    
    def _send_email(self, to_email: str, subject: str, content: str, lead_id: int) -> Dict:
        """Envia e-mail (simulado - integrar com serviço real)"""
        
        # Aqui você integraria com serviços como SendGrid, Mailchimp, etc.
        # Por enquanto, simula o envio
        
        print(f"📧 E-mail enviado para {to_email}")
        print(f"Assunto: {subject}")
        print(f"Lead ID: {lead_id}")
        
        return {
            'success': True,
            'message': 'E-mail enviado com sucesso (simulado)',
            'email_id': f'email_{lead_id}_{datetime.now().timestamp()}'
        }
    
    def _send_linkedin_message(self, profile_url: str, message: str, lead_id: int) -> Dict:
        """Envia mensagem LinkedIn (simulado - integrar com API)"""
        
        print(f"💼 Mensagem LinkedIn enviada para {profile_url}")
        print(f"Lead ID: {lead_id}")
        
        return {
            'success': True,
            'message': 'Mensagem LinkedIn enviada com sucesso (simulado)',
            'message_id': f'linkedin_{lead_id}_{datetime.now().timestamp()}'
        }
    
    def _send_instagram_dm(self, profile_url: str, message: str, lead_id: int) -> Dict:
        """Envia DM Instagram (simulado - integrar com API)"""
        
        print(f"📱 DM Instagram enviado para {profile_url}")
        print(f"Lead ID: {lead_id}")
        
        return {
            'success': True,
            'message': 'DM Instagram enviado com sucesso (simulado)',
            'message_id': f'instagram_{lead_id}_{datetime.now().timestamp()}'
        }
    
    def run_outreach_campaign(self, campaign_config: Dict) -> Dict:
        """
        Executa campanha de contato inicial
        
        Args:
            campaign_config: Configuração da campanha
        
        Returns:
            Dict com resultado da campanha
        """
        
        try:
            # Busca leads qualificados
            min_score = campaign_config.get('min_score', 50)
            max_leads = campaign_config.get('max_leads', 20)
            channels = campaign_config.get('channels', ['email'])
            
            qualified_leads = self.lead_manager.get_qualified_leads(min_score, max_leads)
            
            results = {
                'total_leads': len(qualified_leads),
                'email_sent': 0,
                'linkedin_sent': 0,
                'instagram_sent': 0,
                'errors': []
            }
            
            for lead_data in qualified_leads:
                lead_id = lead_data['id']
                
                try:
                    # Envia e-mail se configurado e disponível
                    if 'email' in channels and lead_data.get('email'):
                        email_result = self.send_initial_email(lead_id)
                        if email_result['success']:
                            results['email_sent'] += 1
                        else:
                            results['errors'].append(f"Lead {lead_id} - Email: {email_result['error']}")
                    
                    # Envia mensagem LinkedIn se configurado e disponível
                    if 'linkedin' in channels and lead_data.get('linkedin_profile'):
                        linkedin_result = self.send_linkedin_message(lead_id)
                        if linkedin_result['success']:
                            results['linkedin_sent'] += 1
                        else:
                            results['errors'].append(f"Lead {lead_id} - LinkedIn: {linkedin_result['error']}")
                    
                    # Envia DM Instagram se configurado e disponível
                    if 'instagram' in channels and lead_data.get('instagram_profile'):
                        instagram_result = self.send_instagram_dm(lead_id)
                        if instagram_result['success']:
                            results['instagram_sent'] += 1
                        else:
                            results['errors'].append(f"Lead {lead_id} - Instagram: {instagram_result['error']}")
                
                except Exception as e:
                    results['errors'].append(f"Lead {lead_id}: {str(e)}")
            
            return {
                'success': True,
                'campaign_results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_follow_up_campaign(self, days_since_contact: int = 7) -> Dict:
        """Executa campanha de follow-up"""
        
        try:
            # Busca leads que precisam de follow-up
            follow_up_leads = self.lead_manager.get_leads_for_follow_up(days_since_contact)
            
            results = {
                'total_leads': len(follow_up_leads),
                'follow_ups_sent': 0,
                'errors': []
            }
            
            for lead_data in follow_up_leads:
                lead_id = lead_data['id']
                
                try:
                    # Prioriza canal que teve melhor resposta anterior
                    last_interactions = self.lead_manager.get_lead_interactions(lead_id)
                    
                    if last_interactions:
                        # Usa o mesmo canal da última interação
                        last_channel = last_interactions[0]['interaction_type']
                        
                        if last_channel == 'email' and lead_data.get('email'):
                            result = self.send_initial_email(lead_id, 'email_follow_up')
                        elif last_channel == 'linkedin' and lead_data.get('linkedin_profile'):
                            result = self.send_linkedin_message(lead_id, 'follow_up')
                        elif last_channel == 'instagram' and lead_data.get('instagram_profile'):
                            result = self.send_instagram_dm(lead_id, 'follow_up')
                        else:
                            # Fallback para e-mail
                            result = self.send_initial_email(lead_id, 'email_follow_up')
                        
                        if result['success']:
                            results['follow_ups_sent'] += 1
                        else:
                            results['errors'].append(f"Lead {lead_id}: {result['error']}")
                
                except Exception as e:
                    results['errors'].append(f"Lead {lead_id}: {str(e)}")
            
            return {
                'success': True,
                'follow_up_results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

