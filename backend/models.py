from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化 SQLAlchemy 实例
db = SQLAlchemy()

# 用户角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model):
    """用户数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 建立与角色的多对多关系
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
        backref=db.backref('users', lazy=True))
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """将模型转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'role_ids': [role.id for role in self.roles],
            'role_names': [role.name for role in self.roles],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Role(db.Model):
    """角色数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """将模型转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_count': len(self.users),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

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
    model_top_p = db.Column(db.Float, nullable=False, default=0.9)  # Top-p参数
    model_top_k = db.Column(db.Integer, nullable=False, default=40)  # Top-k参数
    model_presence_penalty = db.Column(db.Float, nullable=False, default=0.0)  # 存在惩罚
    model_frequency_penalty = db.Column(db.Float, nullable=False, default=0.0)  # 频率惩罚
    model_stop_sequences = db.Column(db.Text, nullable=True)  # 停止序列（用逗号分隔）
    model_context_window = db.Column(db.Integer, nullable=False, default=4096)  # 上下文窗口大小
    model_system_prompt = db.Column(db.Text, nullable=True)  # 系统提示词
    
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
            'model_api_key': self.model_api_key,
            'model_temperature': self.model_temperature,
            'model_max_tokens': self.model_max_tokens,
            'model_top_p': self.model_top_p,
            'model_top_k': self.model_top_k,
            'model_presence_penalty': self.model_presence_penalty,
            'model_frequency_penalty': self.model_frequency_penalty,
            'model_stop_sequences': self.model_stop_sequences.split(',') if self.model_stop_sequences else [],
            'model_context_window': self.model_context_window,
            'model_system_prompt': self.model_system_prompt,
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
