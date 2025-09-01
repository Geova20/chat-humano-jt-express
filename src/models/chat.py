from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_ip = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, ended, transferred
    satisfaction_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    
    # Relacionamento com mensagens
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'status': self.status,
            'satisfaction_rating': self.satisfaction_rating,
            'message_count': len(self.messages)
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.session_id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # user, bot, system
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float, nullable=True)  # tempo de resposta em segundos
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'response_time': self.response_time
        }

class ChatAnalytics(db.Model):
    __tablename__ = 'chat_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total_sessions = db.Column(db.Integer, default=0)
    total_messages = db.Column(db.Integer, default=0)
    avg_session_duration = db.Column(db.Float, default=0.0)  # em minutos
    avg_response_time = db.Column(db.Float, default=0.0)  # em segundos
    satisfaction_avg = db.Column(db.Float, default=0.0)
    common_issues = db.Column(db.Text, nullable=True)  # JSON string
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_sessions': self.total_sessions,
            'total_messages': self.total_messages,
            'avg_session_duration': self.avg_session_duration,
            'avg_response_time': self.avg_response_time,
            'satisfaction_avg': self.satisfaction_avg,
            'common_issues': self.common_issues
        }

