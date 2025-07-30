import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.models.lead import db, Lead, LeadInteraction, LeadSource

class LeadManager:
    """Gerencia leads e prospecção de PMEs"""
    
    def __init__(self):
        pass
    
    def create_lead(self, lead_data: Dict) -> Dict:
        """
        Cria um novo lead
        
        Args:
            lead_data: Dados do lead
        
        Returns:
            Dict com resultado da criação
        """
        
        try:
            # Verifica se já existe lead com mesmo CNPJ
            if lead_data.get('cnpj'):
                existing_lead = Lead.query.filter_by(cnpj=lead_data['cnpj']).first()
                if existing_lead:
                    return {
                        'success': False,
                        'error': 'Lead já existe com este CNPJ',
                        'existing_lead_id': existing_lead.id
                    }
            
            # Cria novo lead
            lead = Lead(
                company_name=lead_data['company_name'],
                cnpj=lead_data.get('cnpj'),
                sector=lead_data.get('sector'),
                company_size=lead_data.get('company_size'),
                annual_revenue=lead_data.get('annual_revenue'),
                employee_count=lead_data.get('employee_count'),
                contact_name=lead_data.get('contact_name'),
                contact_position=lead_data.get('contact_position'),
                email=lead_data.get('email'),
                phone=lead_data.get('phone'),
                website=lead_data.get('website'),
                linkedin_profile=lead_data.get('linkedin_profile'),
                instagram_profile=lead_data.get('instagram_profile'),
                city=lead_data.get('city'),
                state=lead_data.get('state'),
                address=lead_data.get('address'),
                source=lead_data.get('source', 'manual'),
                tax_regime=lead_data.get('tax_regime'),
                estimated_recovery_potential=lead_data.get('estimated_recovery_potential')
            )
            
            # Define dados adicionais se fornecidos
            if 'additional_data' in lead_data:
                lead.set_additional_data(lead_data['additional_data'])
            
            # Calcula score de qualificação
            lead.calculate_score()
            
            db.session.add(lead)
            db.session.commit()
            
            return {
                'success': True,
                'lead_id': lead.id,
                'score': lead.score,
                'message': 'Lead criado com sucesso'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_lead(self, lead_id: int, update_data: Dict) -> Dict:
        """Atualiza dados de um lead"""
        
        try:
            lead = Lead.query.get(lead_id)
            if not lead:
                return {'success': False, 'error': 'Lead não encontrado'}
            
            # Atualiza campos fornecidos
            for field, value in update_data.items():
                if hasattr(lead, field) and field != 'id':
                    setattr(lead, field, value)
            
            # Recalcula score se dados relevantes foram alterados
            score_fields = ['sector', 'company_size', 'annual_revenue', 'tax_regime', 'email', 'phone', 'linkedin_profile']
            if any(field in update_data for field in score_fields):
                lead.calculate_score()
            
            lead.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Lead atualizado com sucesso',
                'new_score': lead.score
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_qualified_leads(self, min_score: int = 50, limit: int = 50) -> List[Dict]:
        """Retorna leads qualificados para contato"""
        
        leads = Lead.query.filter(
            Lead.score >= min_score,
            Lead.status.in_(['new', 'contacted'])
        ).order_by(Lead.score.desc()).limit(limit).all()
        
        return [lead.to_dict() for lead in leads]
    
    def search_leads_by_sector(self, sector: str, min_score: int = 30) -> List[Dict]:
        """Busca leads por setor específico"""
        
        leads = Lead.query.filter(
            Lead.sector == sector,
            Lead.score >= min_score
        ).order_by(Lead.score.desc()).all()
        
        return [lead.to_dict() for lead in leads]
    
    def import_leads_from_cnpj_api(self, cnpj_list: List[str], source_name: str = 'cnpj_api') -> Dict:
        """
        Importa leads usando API de consulta CNPJ
        
        Args:
            cnpj_list: Lista de CNPJs para consultar
            source_name: Nome da fonte dos leads
        
        Returns:
            Dict com resultado da importação
        """
        
        imported_count = 0
        errors = []
        
        for cnpj in cnpj_list:
            try:
                # Consulta API de CNPJ (exemplo usando ReceitaWS)
                company_data = self._fetch_company_data_from_cnpj(cnpj)
                
                if company_data:
                    # Mapeia dados da API para formato do lead
                    lead_data = self._map_cnpj_data_to_lead(company_data, source_name)
                    
                    # Cria lead
                    result = self.create_lead(lead_data)
                    
                    if result['success']:
                        imported_count += 1
                    else:
                        errors.append(f"CNPJ {cnpj}: {result['error']}")
                else:
                    errors.append(f"CNPJ {cnpj}: Dados não encontrados")
                    
            except Exception as e:
                errors.append(f"CNPJ {cnpj}: {str(e)}")
        
        return {
            'success': True,
            'imported_count': imported_count,
            'total_processed': len(cnpj_list),
            'errors': errors
        }
    
    def _fetch_company_data_from_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Busca dados da empresa via API de CNPJ"""
        
        try:
            # Remove formatação do CNPJ
            clean_cnpj = ''.join(filter(str.isdigit, cnpj))
            
            # Consulta ReceitaWS (API gratuita)
            url = f"https://www.receitaws.com.br/v1/cnpj/{clean_cnpj}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK':
                    return data
            
            return None
            
        except Exception as e:
            print(f"Erro ao consultar CNPJ {cnpj}: {e}")
            return None
    
    def _map_cnpj_data_to_lead(self, cnpj_data: Dict, source: str) -> Dict:
        """Mapeia dados da API de CNPJ para formato do lead"""
        
        # Mapeia porte da empresa
        porte_map = {
            'MICRO EMPRESA': 'Micro',
            'EMPRESA DE PEQUENO PORTE': 'Pequena',
            'DEMAIS': 'Média'
        }
        
        # Mapeia setor baseado na atividade principal
        sector = self._classify_sector_from_activity(cnpj_data.get('atividade_principal', [{}])[0].get('text', ''))
        
        return {
            'company_name': cnpj_data.get('nome', ''),
            'cnpj': cnpj_data.get('cnpj', ''),
            'sector': sector,
            'company_size': porte_map.get(cnpj_data.get('porte', ''), 'Não informado'),
            'contact_name': None,  # Não disponível na API
            'email': cnpj_data.get('email'),
            'phone': cnpj_data.get('telefone'),
            'website': None,  # Não disponível na API
            'city': cnpj_data.get('municipio'),
            'state': cnpj_data.get('uf'),
            'address': f"{cnpj_data.get('logradouro', '')}, {cnpj_data.get('numero', '')} - {cnpj_data.get('bairro', '')}",
            'source': source,
            'additional_data': {
                'situacao': cnpj_data.get('situacao'),
                'data_situacao': cnpj_data.get('data_situacao'),
                'atividade_principal': cnpj_data.get('atividade_principal'),
                'atividades_secundarias': cnpj_data.get('atividades_secundarias'),
                'capital_social': cnpj_data.get('capital_social')
            }
        }
    
    def _classify_sector_from_activity(self, activity_text: str) -> str:
        """Classifica setor baseado na atividade principal"""
        
        activity_lower = activity_text.lower()
        
        if any(word in activity_lower for word in ['indústria', 'fabricação', 'manufatura', 'produção']):
            return 'Indústria'
        elif any(word in activity_lower for word in ['comércio', 'venda', 'varejo', 'atacado']):
            return 'Comércio'
        elif any(word in activity_lower for word in ['serviços', 'consultoria', 'assessoria']):
            return 'Serviços'
        elif any(word in activity_lower for word in ['construção', 'obras', 'engenharia']):
            return 'Construção'
        elif any(word in activity_lower for word in ['tecnologia', 'software', 'informática']):
            return 'Tecnologia'
        else:
            return 'Outros'
    
    def record_interaction(self, lead_id: int, interaction_data: Dict) -> Dict:
        """Registra uma interação com o lead"""
        
        try:
            interaction = LeadInteraction(
                lead_id=lead_id,
                interaction_type=interaction_data['interaction_type'],
                channel=interaction_data.get('channel'),
                subject=interaction_data.get('subject'),
                message=interaction_data.get('message'),
                status=interaction_data.get('status', 'sent')
            )
            
            if 'metadata' in interaction_data:
                interaction.set_metadata(interaction_data['metadata'])
            
            db.session.add(interaction)
            
            # Atualiza último contato do lead
            lead = Lead.query.get(lead_id)
            if lead:
                lead.last_contact_at = datetime.utcnow()
                if lead.status == 'new':
                    lead.status = 'contacted'
            
            db.session.commit()
            
            return {
                'success': True,
                'interaction_id': interaction.id,
                'message': 'Interação registrada com sucesso'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_lead_interactions(self, lead_id: int) -> List[Dict]:
        """Retorna histórico de interações de um lead"""
        
        interactions = LeadInteraction.query.filter_by(lead_id=lead_id).order_by(
            LeadInteraction.sent_at.desc()
        ).all()
        
        return [interaction.to_dict() for interaction in interactions]
    
    def get_leads_for_follow_up(self, days_since_last_contact: int = 7) -> List[Dict]:
        """Retorna leads que precisam de follow-up"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_since_last_contact)
        
        leads = Lead.query.filter(
            Lead.status == 'contacted',
            Lead.last_contact_at <= cutoff_date
        ).order_by(Lead.score.desc()).all()
        
        return [lead.to_dict() for lead in leads]
    
    def get_lead_statistics(self) -> Dict:
        """Retorna estatísticas dos leads"""
        
        total_leads = Lead.query.count()
        new_leads = Lead.query.filter_by(status='new').count()
        contacted_leads = Lead.query.filter_by(status='contacted').count()
        qualified_leads = Lead.query.filter(Lead.score >= 50).count()
        
        # Leads por setor
        sectors = db.session.query(Lead.sector, db.func.count(Lead.id)).group_by(Lead.sector).all()
        sector_stats = {sector: count for sector, count in sectors if sector}
        
        # Leads por fonte
        sources = db.session.query(Lead.source, db.func.count(Lead.id)).group_by(Lead.source).all()
        source_stats = {source: count for source, count in sources if source}
        
        return {
            'total_leads': total_leads,
            'new_leads': new_leads,
            'contacted_leads': contacted_leads,
            'qualified_leads': qualified_leads,
            'conversion_rate': round((qualified_leads / total_leads * 100) if total_leads > 0 else 0, 2),
            'sectors': sector_stats,
            'sources': source_stats
        }

