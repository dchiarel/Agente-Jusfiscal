from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.lead import db, Lead, LeadInteraction, LeadSource
from src.services.lead_manager import LeadManager
from src.services.outreach_manager import OutreachManager

lead_bp = Blueprint('lead', __name__)

@lead_bp.route('/leads', methods=['GET'])
def get_leads():
    """Retorna lista de leads com filtros opcionais"""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    sector = request.args.get('sector')
    min_score = request.args.get('min_score', type=int)
    
    query = Lead.query
    
    if status:
        query = query.filter_by(status=status)
    if sector:
        query = query.filter_by(sector=sector)
    if min_score:
        query = query.filter(Lead.score >= min_score)
    
    leads = query.order_by(Lead.score.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'leads': [lead.to_dict() for lead in leads.items],
        'total': leads.total,
        'pages': leads.pages,
        'current_page': page
    })

@lead_bp.route('/leads', methods=['POST'])
def create_lead():
    """Cria um novo lead"""
    
    data = request.get_json()
    
    manager = LeadManager()
    result = manager.create_lead(data)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@lead_bp.route('/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    """Retorna dados de um lead específico"""
    
    lead = Lead.query.get_or_404(lead_id)
    
    # Inclui histórico de interações
    manager = LeadManager()
    interactions = manager.get_lead_interactions(lead_id)
    
    lead_data = lead.to_dict()
    lead_data['interactions'] = interactions
    
    return jsonify(lead_data)

@lead_bp.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Atualiza dados de um lead"""
    
    data = request.get_json()
    
    manager = LeadManager()
    result = manager.update_lead(lead_id, data)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@lead_bp.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Remove um lead"""
    
    lead = Lead.query.get_or_404(lead_id)
    
    db.session.delete(lead)
    db.session.commit()
    
    return jsonify({'message': 'Lead removido com sucesso'})

@lead_bp.route('/leads/import-cnpj', methods=['POST'])
def import_leads_from_cnpj():
    """Importa leads a partir de lista de CNPJs"""
    
    data = request.get_json()
    cnpj_list = data.get('cnpj_list', [])
    source_name = data.get('source_name', 'cnpj_import')
    
    if not cnpj_list:
        return jsonify({'error': 'Lista de CNPJs é obrigatória'}), 400
    
    manager = LeadManager()
    result = manager.import_leads_from_cnpj_api(cnpj_list, source_name)
    
    return jsonify(result)

@lead_bp.route('/leads/qualified', methods=['GET'])
def get_qualified_leads():
    """Retorna leads qualificados para contato"""
    
    min_score = request.args.get('min_score', 50, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    manager = LeadManager()
    qualified_leads = manager.get_qualified_leads(min_score, limit)
    
    return jsonify({
        'qualified_leads': qualified_leads,
        'count': len(qualified_leads)
    })

@lead_bp.route('/leads/by-sector/<sector>', methods=['GET'])
def get_leads_by_sector(sector):
    """Retorna leads de um setor específico"""
    
    min_score = request.args.get('min_score', 30, type=int)
    
    manager = LeadManager()
    sector_leads = manager.search_leads_by_sector(sector, min_score)
    
    return jsonify({
        'sector': sector,
        'leads': sector_leads,
        'count': len(sector_leads)
    })

@lead_bp.route('/leads/follow-up', methods=['GET'])
def get_leads_for_follow_up():
    """Retorna leads que precisam de follow-up"""
    
    days = request.args.get('days', 7, type=int)
    
    manager = LeadManager()
    follow_up_leads = manager.get_leads_for_follow_up(days)
    
    return jsonify({
        'follow_up_leads': follow_up_leads,
        'count': len(follow_up_leads),
        'days_since_contact': days
    })

@lead_bp.route('/leads/<int:lead_id>/interactions', methods=['POST'])
def record_interaction(lead_id):
    """Registra uma interação com o lead"""
    
    data = request.get_json()
    
    manager = LeadManager()
    result = manager.record_interaction(lead_id, data)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@lead_bp.route('/leads/<int:lead_id>/interactions', methods=['GET'])
def get_lead_interactions(lead_id):
    """Retorna histórico de interações de um lead"""
    
    manager = LeadManager()
    interactions = manager.get_lead_interactions(lead_id)
    
    return jsonify({
        'lead_id': lead_id,
        'interactions': interactions,
        'count': len(interactions)
    })

@lead_bp.route('/leads/statistics', methods=['GET'])
def get_lead_statistics():
    """Retorna estatísticas dos leads"""
    
    manager = LeadManager()
    stats = manager.get_lead_statistics()
    
    return jsonify(stats)

# Rotas para outreach/contato inicial

@lead_bp.route('/outreach/email/<int:lead_id>', methods=['POST'])
def send_initial_email(lead_id):
    """Envia e-mail inicial para um lead"""
    
    data = request.get_json()
    template_type = data.get('template_type', 'email')
    
    outreach = OutreachManager()
    result = outreach.send_initial_email(lead_id, template_type)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@lead_bp.route('/outreach/linkedin/<int:lead_id>', methods=['POST'])
def send_linkedin_message(lead_id):
    """Envia mensagem LinkedIn para um lead"""
    
    data = request.get_json()
    message_type = data.get('message_type', 'initial')
    
    outreach = OutreachManager()
    result = outreach.send_linkedin_message(lead_id, message_type)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@lead_bp.route('/outreach/instagram/<int:lead_id>', methods=['POST'])
def send_instagram_dm(lead_id):
    """Envia DM Instagram para um lead"""
    
    data = request.get_json()
    message_type = data.get('message_type', 'initial')
    
    outreach = OutreachManager()
    result = outreach.send_instagram_dm(lead_id, message_type)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@lead_bp.route('/outreach/campaign', methods=['POST'])
def run_outreach_campaign():
    """Executa campanha de contato inicial"""
    
    data = request.get_json()
    
    outreach = OutreachManager()
    result = outreach.run_outreach_campaign(data)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@lead_bp.route('/outreach/follow-up', methods=['POST'])
def run_follow_up_campaign():
    """Executa campanha de follow-up"""
    
    data = request.get_json()
    days_since_contact = data.get('days_since_contact', 7)
    
    outreach = OutreachManager()
    result = outreach.run_follow_up_campaign(days_since_contact)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

# Rotas para fontes de leads

@lead_bp.route('/lead-sources', methods=['GET'])
def get_lead_sources():
    """Retorna fontes de leads configuradas"""
    
    sources = LeadSource.query.all()
    
    return jsonify([source.to_dict() for source in sources])

@lead_bp.route('/lead-sources', methods=['POST'])
def create_lead_source():
    """Cria uma nova fonte de leads"""
    
    data = request.get_json()
    
    source = LeadSource(
        name=data['name'],
        source_type=data['source_type'],
        is_active=data.get('is_active', True)
    )
    
    if 'config' in data:
        source.set_config(data['config'])
    
    db.session.add(source)
    db.session.commit()
    
    return jsonify({
        'id': source.id,
        'message': 'Fonte de leads criada com sucesso'
    }), 201

@lead_bp.route('/lead-sources/<int:source_id>', methods=['PUT'])
def update_lead_source(source_id):
    """Atualiza configuração de uma fonte de leads"""
    
    source = LeadSource.query.get_or_404(source_id)
    data = request.get_json()
    
    if 'name' in data:
        source.name = data['name']
    if 'is_active' in data:
        source.is_active = data['is_active']
    if 'config' in data:
        source.set_config(data['config'])
    
    source.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Fonte de leads atualizada com sucesso'})

