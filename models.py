from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化 SQLAlchemy 实例
db = SQLAlchemy()

class Agent(db.Model):
    """智能体数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='inactive')  # inactive, running, paused, stopped
    
    # 模型配置
    model_name = db.Column(db.String(100), nullable=False, default='llama2')  # Ollama模型名称
    model_provider = db.Column(db.String(50), nullable=False, default='ollama')  # 模型提供商：ollama, openai等
    model_api_url = db.Column(db.String(200), nullable=False, default='http://localhost:11434/v1')  # 模型API地址
    model_api_key = db.Column(db.String(200), nullable=True)  # API密钥（OpenAI需要）
    model_temperature = db.Column(db.Float, nullable=False, default=0.7)  # 温度参数
    model_max_tokens = db.Column(db.Integer, nullable=False, default=2048)  # 最大 tokens
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 建立与日志的一对多关系
    logs = db.relationship('AgentLog', backref='agent', lazy=True)
    # 建立与会话的一对多关系
    conversations = db.relationship('Conversation', backref='agent', lazy=True)
    
    def to_dict(self):
        """将模型转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'model_name': self.model_name,
            'model_provider': self.model_provider,
            'model_api_url': self.model_api_url,
            'model_temperature': self.model_temperature,
            'model_max_tokens': self.model_max_tokens,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Conversation(db.Model):
    """会话数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    conversation_id = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 建立与消息的一对多关系
    messages = db.relationship('Message', backref='conversation', lazy=True)
    
    def to_dict(self):
        """将模型转换为字典格式"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'conversation_id': self.conversation_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Message(db.Model):
    """消息数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """将模型转换为字典格式"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

class AgentLog(db.Model):
    """智能体日志数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # info, warning, error, debug
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """将模型转换为字典格式"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'level': self.level,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }
