from flask import Blueprint, request, jsonify
from datetime import datetime
from src.services.scheduler import scheduler

scheduler_bp = Blueprint('scheduler', __name__)

@scheduler_bp.route('/start', methods=['POST'])
def start_scheduler():
    """Inicia o agendador de tarefas"""
    try:
        scheduler.start()
        return jsonify({'message': 'Agendador iniciado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scheduler_bp.route('/stop', methods=['POST'])
def stop_scheduler():
    """Para o agendador de tarefas"""
    try:
        scheduler.stop()
        return jsonify({'message': 'Agendador parado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scheduler_bp.route('/status', methods=['GET'])
def get_scheduler_status():
    """Retorna o status do agendador"""
    status = scheduler.get_scheduler_status()
    return jsonify(status)

@scheduler_bp.route('/schedule-content', methods=['POST'])
def schedule_content_generation():
    """Agenda geração de conteúdo específico"""
    data = request.get_json()
    
    scheduled_time = None
    if 'scheduled_time' in data:
        scheduled_time = datetime.fromisoformat(data['scheduled_time'])
    
    result = scheduler.schedule_content_generation(
        topic=data['topic'],
        content_type=data['content_type'],
        target_sector=data.get('target_sector'),
        scheduled_time=scheduled_time
    )
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

