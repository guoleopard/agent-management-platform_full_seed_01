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
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 建立与日志的一对多关系
    logs = db.relationship('AgentLog', backref='agent', lazy=True)
    
    def to_dict(self):
        """将模型转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
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
