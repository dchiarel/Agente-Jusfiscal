from src.models.user import db
from datetime import datetime
import json

class PublicationChannel(db.Model):
    __tablename__ = 'publication_channels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    channel_type = db.Column(db.String(50), nullable=False)  # 'linkedin', 'wordpress', 'email'
    api_config = db.Column(db.Text)  # JSON string with API configuration
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_api_config(self):
        return json.loads(self.api_config) if self.api_config else {}
    
    def set_api_config(self, config_dict):
        self.api_config = json.dumps(config_dict)

class ScheduledPublication(db.Model):
    __tablename__ = 'scheduled_publications'
    
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('generated_content.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('publication_channels.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'published', 'failed', 'cancelled'
    published_at = db.Column(db.DateTime)
    publication_url = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    content = db.relationship('GeneratedContent', backref='scheduled_publications')
    channel = db.relationship('PublicationChannel', backref='scheduled_publications')

class PublicationLog(db.Model):
    __tablename__ = 'publication_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('generated_content.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('publication_channels.id'), nullable=False)
    publication_status = db.Column(db.String(20), nullable=False)  # 'success', 'failed'
    publication_url = db.Column(db.String(500))
    response_data = db.Column(db.Text)  # JSON string with API response
    error_message = db.Column(db.Text)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    content = db.relationship('GeneratedContent', backref='publication_logs')
    channel = db.relationship('PublicationChannel', backref='publication_logs')
    
    def get_response_data(self):
        return json.loads(self.response_data) if self.response_data else {}
    
    def set_response_data(self, data_dict):
        self.response_data = json.dumps(data_dict)

