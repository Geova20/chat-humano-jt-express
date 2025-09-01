from flask import Blueprint, request, jsonify
from src.models.chat import db, ChatSession, ChatMessage, ChatAnalytics
from datetime import datetime, date
import uuid
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/session', methods=['POST'])
def create_chat_session():
    """Criar nova sessão de chat"""
    try:
        data = request.get_json() or {}
        
        session_id = str(uuid.uuid4())
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        new_session = ChatSession(
            session_id=session_id,
            user_ip=user_ip,
            user_agent=user_agent
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Sessão de chat criada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar sessão: {str(e)}'
        }), 500

@chat_bp.route('/chat/message', methods=['POST'])
def send_message():
    """Enviar mensagem no chat"""
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'message': 'session_id e content são obrigatórios'
            }), 400
        
        session_id = data['session_id']
        content = data['content']
        message_type = data.get('message_type', 'user')
        
        # Verificar se a sessão existe
        session = ChatSession.query.filter_by(session_id=session_id).first()
        if not session:
            return jsonify({
                'success': False,
                'message': 'Sessão não encontrada'
            }), 404
        
        # Criar nova mensagem
        new_message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        # Gerar resposta automática se for mensagem do usuário
        bot_response = None
        if message_type == 'user':
            bot_response = generate_bot_response(content)
            
            bot_message = ChatMessage(
                session_id=session_id,
                message_type='bot',
                content=bot_response,
                response_time=1.5  # Simular tempo de resposta
            )
            
            db.session.add(bot_message)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': new_message.to_dict(),
            'bot_response': bot_response
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar mensagem: {str(e)}'
        }), 500

@chat_bp.route('/chat/session/<session_id>/messages', methods=['GET'])
def get_session_messages(session_id):
    """Obter mensagens de uma sessão"""
    try:
        session = ChatSession.query.filter_by(session_id=session_id).first()
        if not session:
            return jsonify({
                'success': False,
                'message': 'Sessão não encontrada'
            }), 404
        
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar mensagens: {str(e)}'
        }), 500

@chat_bp.route('/chat/session/<session_id>/end', methods=['POST'])
def end_chat_session(session_id):
    """Finalizar sessão de chat"""
    try:
        data = request.get_json() or {}
        
        session = ChatSession.query.filter_by(session_id=session_id).first()
        if not session:
            return jsonify({
                'success': False,
                'message': 'Sessão não encontrada'
            }), 404
        
        session.ended_at = datetime.utcnow()
        session.status = 'ended'
        
        # Salvar avaliação se fornecida
        if 'satisfaction_rating' in data:
            rating = data['satisfaction_rating']
            if 1 <= rating <= 5:
                session.satisfaction_rating = rating
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sessão finalizada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao finalizar sessão: {str(e)}'
        }), 500

@chat_bp.route('/chat/analytics', methods=['GET'])
def get_chat_analytics():
    """Obter analytics do chat"""
    try:
        # Estatísticas gerais
        total_sessions = ChatSession.query.count()
        total_messages = ChatMessage.query.count()
        
        # Sessões ativas
        active_sessions = ChatSession.query.filter_by(status='active').count()
        
        # Avaliações
        ratings = db.session.query(ChatSession.satisfaction_rating).filter(
            ChatSession.satisfaction_rating.isnot(None)
        ).all()
        
        avg_rating = 0
        if ratings:
            avg_rating = sum(r[0] for r in ratings) / len(ratings)
        
        # Problemas mais comuns (baseado nas mensagens)
        common_issues = analyze_common_issues()
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'active_sessions': active_sessions,
                'average_satisfaction': round(avg_rating, 2),
                'total_ratings': len(ratings),
                'common_issues': common_issues
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar analytics: {str(e)}'
        }), 500

def generate_bot_response(user_message):
    """Gerar resposta automática do bot"""
    message_lower = user_message.lower()
    
    responses = {
        'rastrear': [
            'Para rastrear sua encomenda, preciso do código de rastreamento. Você pode me informar o código que começa com JT?',
            'Claro! Vou ajudar você a rastrear sua encomenda. Por favor, me informe o código de rastreamento.'
        ],
        'entrega': [
            'Entendo sua preocupação com a entrega. Pode me contar mais detalhes sobre o problema que está enfrentando?',
            'Vou verificar o que aconteceu com sua entrega. Você pode me informar o código de rastreamento e seu endereço?'
        ],
        'endereço': [
            'Para alterar o endereço de entrega, preciso verificar se ainda é possível fazer essa alteração. Me informe o código de rastreamento, por favor.',
            'Vou ajudar você a alterar o endereço. Primeiro, preciso do código de rastreamento da sua encomenda.'
        ],
        'supervisor': [
            'Vou transferir você para um supervisor agora mesmo. Por favor, aguarde um momento.',
            'Entendo que precisa falar com um supervisor. Vou fazer a transferência imediatamente.'
        ],
        'problema': [
            'Sinto muito pelo inconveniente. Pode me explicar qual problema está enfrentando para que eu possa ajudar?',
            'Vou resolver isso para você! Me conte mais detalhes sobre o problema.'
        ]
    }
    
    # Verificar palavras-chave
    for keyword, response_list in responses.items():
        if keyword in message_lower:
            import random
            return random.choice(response_list)
    
    # Resposta padrão
    default_responses = [
        'Entendi. Vou verificar essa informação para você. Um momento, por favor.',
        'Obrigado pela informação. Deixe-me consultar nosso sistema.',
        'Perfeito! Vou processar sua solicitação agora.',
        'Compreendo sua situação. Vou fazer o possível para resolver isso rapidamente.',
        'Essa é uma ótima pergunta! Vou buscar a resposta mais precisa para você.'
    ]
    
    import random
    return random.choice(default_responses)

def analyze_common_issues():
    """Analisar problemas mais comuns baseado nas mensagens"""
    try:
        # Buscar mensagens dos últimos 30 dias
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        messages = ChatMessage.query.filter(
            ChatMessage.message_type == 'user',
            ChatMessage.timestamp >= thirty_days_ago
        ).all()
        
        issue_keywords = {
            'rastreamento': ['rastrear', 'código', 'jt', 'localizar'],
            'entrega': ['entrega', 'entregar', 'receber', 'atraso'],
            'endereço': ['endereço', 'endereco', 'alterar', 'mudar'],
            'atendimento': ['atendimento', 'suporte', 'ajuda', 'problema'],
            'supervisor': ['supervisor', 'gerente', 'responsável']
        }
        
        issue_counts = {issue: 0 for issue in issue_keywords.keys()}
        
        for message in messages:
            content_lower = message.content.lower()
            for issue, keywords in issue_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    issue_counts[issue] += 1
        
        # Ordenar por frequência
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{'issue': issue, 'count': count} for issue, count in sorted_issues if count > 0]
        
    except Exception as e:
        return []

