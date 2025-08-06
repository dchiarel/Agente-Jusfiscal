from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.content import db, ContentTemplate, GeneratedContent, ContentTopic
from src.services.content_generator import ContentGenerator
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

content_bp = Blueprint('content', __name__)

@content_bp.route('/templates', methods=['GET'])
def get_templates():
    """Retorna todos os templates de conteúdo"""
    templates = ContentTemplate.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'content_type': t.content_type,
        'template_content': t.template_content,
        'variables': t.get_variables(),
        'created_at': t.created_at.isoformat()
    } for t in templates])

@content_bp.route('/templates', methods=['POST'])
def create_template():
    """Cria um novo template de conteúdo"""
    data = request.get_json()
    
    template = ContentTemplate(
        name=data['name'],
        content_type=data['content_type'],
        template_content=data['template_content']
    )
    
    if 'variables' in data:
        template.set_variables(data['variables'])
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({'id': template.id, 'message': 'Template criado com sucesso'}), 201

@content_bp.route('/generate', methods=['POST'])
def generate_content():
    """Gera conteúdo automaticamente"""
    data = request.get_json()
    
    generator = ContentGenerator()
    
    try:
        content = generator.generate_content(
            content_type=data['content_type'],
            topic=data['topic'],
            target_sector=data.get('target_sector'),
            template_id=data.get('template_id')
        )
        
        # Salva o conteúdo gerado
        generated_content = GeneratedContent(
            title=content['title'],
            content=content['content'],
            content_type=data['content_type'],
            target_sector=data.get('target_sector'),
            template_id=data.get('template_id')
        )
        
        if 'keywords' in content:
            generated_content.set_keywords(content['keywords'])
        
        db.session.add(generated_content)
        db.session.commit()
        
        return jsonify({
            'id': generated_content.id,
            'title': content['title'],
            'content': content['content'],
            'keywords': content.get('keywords', []),
            'message': 'Conteúdo gerado com sucesso'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content', methods=['GET'])
def get_content():
    """Retorna todo o conteúdo gerado"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    content_type = request.args.get('content_type')
    status = request.args.get('status')
    
    query = GeneratedContent.query
    
    if content_type:
        query = query.filter_by(content_type=content_type)
    if status:
        query = query.filter_by(status=status)
    
    content = query.order_by(GeneratedContent.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'content': [{
            'id': c.id,
            'title': c.title,
            'content': c.content,
            'content_type': c.content_type,
            'target_sector': c.target_sector,
            'keywords': c.get_keywords(),
            'status': c.status,
            'created_at': c.created_at.isoformat(),
            'published_at': c.published_at.isoformat() if c.published_at else None
        } for c in content.items],
        'total': content.total,
        'pages': content.pages,
        'current_page': page
    })

@content_bp.route('/content/<int:content_id>', methods=['PUT'])
def update_content_status(content_id):
    """Atualiza o status do conteúdo"""
    content = GeneratedContent.query.get_or_404(content_id)
    data = request.get_json()
    
    if 'status' in data:
        content.status = data['status']
        if data['status'] == 'published':
            content.published_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Status atualizado com sucesso'})

@content_bp.route('/topics', methods=['GET'])
def get_topics():
    """Retorna todos os tópicos de conteúdo"""
    topics = ContentTopic.query.order_by(ContentTopic.priority.desc()).all()
    return jsonify([{
        'id': t.id,
        'topic': t.topic,
        'category': t.category,
        'target_sectors': t.get_target_sectors(),
        'keywords': t.get_keywords(),
        'priority': t.priority
    } for t in topics])

@content_bp.route('/topics', methods=['POST'])
def create_topic():
    """Cria um novo tópico de conteúdo"""
    data = request.get_json()
    
    topic = ContentTopic(
        topic=data['topic'],
        category=data['category'],
        priority=data.get('priority', 1)
    )
    
    if 'target_sectors' in data:
        topic.set_target_sectors(data['target_sectors'])
    if 'keywords' in data:
        topic.set_keywords(data['keywords'])
    
    db.session.add(topic)
    db.session.commit()
    
    return jsonify({'id': topic.id, 'message': 'Tópico criado com sucesso'}), 201

