from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from models import db, Agent, AgentLog, Conversation, Message
from datetime import datetime
import os
import requests
import uuid
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)

# 配置 API 文档
api = Api(app, 
          version='1.0', 
          title='Agent Management Platform API',
          description='智能体管理平台 API 文档',
          doc='/docs'  # 文档访问路径
         )

# 创建命名空间
ns_agents = api.namespace('agents', description='智能体管理')
ns_conversations = api.namespace('conversations', description='会话管理')
ns_logs = api.namespace('logs', description='日志管理')

# 定义数据模型
agent_model = api.model('Agent', {
    'id': fields.Integer(readonly=True, description='智能体ID'),
    'name': fields.String(required=True, description='智能体名称'),
    'description': fields.String(description='智能体描述'),
    'status': fields.String(description='智能体状态', enum=['inactive', 'running', 'paused', 'stopped']),
    'model_name': fields.String(description='模型名称'),
    'model_provider': fields.String(description='模型提供商'),
    'model_api_url': fields.String(description='模型API地址'),
    'model_api_key': fields.String(description='模型API密钥'),
    'model_temperature': fields.Float(description='温度参数'),
    'model_max_tokens': fields.Integer(description='最大tokens'),
    'model_top_p': fields.Float(description='Top-p参数'),
    'model_top_k': fields.Integer(description='Top-k参数'),
    'model_presence_penalty': fields.Float(description='存在惩罚'),
    'model_frequency_penalty': fields.Float(description='频率惩罚'),
    'model_stop_sequences': fields.List(fields.String, description='停止序列'),
    'model_context_window': fields.Integer(description='上下文窗口大小'),
    'model_system_prompt': fields.String(description='系统提示词'),
    'created_at': fields.DateTime(readonly=True, description='创建时间'),
    'updated_at': fields.DateTime(readonly=True, description='更新时间')
})

conversation_model = api.model('Conversation', {
    'id': fields.Integer(readonly=True, description='会话ID'),
    'agent_id': fields.Integer(description='智能体ID'),
    'conversation_id': fields.String(readonly=True, description='会话唯一标识'),
    'created_at': fields.DateTime(readonly=True, description='创建时间'),
    'updated_at': fields.DateTime(readonly=True, description='更新时间')
})

message_model = api.model('Message', {
    'id': fields.Integer(readonly=True, description='消息ID'),
    'conversation_id': fields.Integer(description='会话ID'),
    'role': fields.String(description='消息角色', enum=['user', 'assistant', 'system']),
    'content': fields.String(description='消息内容'),
    'created_at': fields.DateTime(readonly=True, description='创建时间')
})

log_model = api.model('AgentLog', {
    'id': fields.Integer(readonly=True, description='日志ID'),
    'agent_id': fields.Integer(description='智能体ID'),
    'level': fields.String(description='日志级别', enum=['info', 'warning', 'error', 'debug']),
    'message': fields.String(description='日志消息'),
    'created_at': fields.DateTime(readonly=True, description='创建时间')
})

# 创建智能体请求模型
create_agent_model = api.model('CreateAgent', {
    'name': fields.String(required=True, description='智能体名称'),
    'description': fields.String(description='智能体描述'),
    'status': fields.String(description='智能体状态', enum=['inactive', 'running', 'paused', 'stopped']),
    'model_name': fields.String(description='模型名称'),
    'model_provider': fields.String(description='模型提供商'),
    'model_api_url': fields.String(description='模型API地址'),
    'model_api_key': fields.String(description='模型API密钥'),
    'model_temperature': fields.Float(description='温度参数'),
    'model_max_tokens': fields.Integer(description='最大tokens'),
    'model_top_p': fields.Float(description='Top-p参数'),
    'model_top_k': fields.Integer(description='Top-k参数'),
    'model_presence_penalty': fields.Float(description='存在惩罚'),
    'model_frequency_penalty': fields.Float(description='频率惩罚'),
    'model_stop_sequences': fields.List(fields.String, description='停止序列'),
    'model_context_window': fields.Integer(description='上下文窗口大小'),
    'model_system_prompt': fields.String(description='系统提示词')
})

# 更新智能体请求模型
update_agent_model = api.model('UpdateAgent', {
    'name': fields.String(description='智能体名称'),
    'description': fields.String(description='智能体描述'),
    'status': fields.String(description='智能体状态', enum=['inactive', 'running', 'paused', 'stopped']),
    'model_name': fields.String(description='模型名称'),
    'model_provider': fields.String(description='模型提供商'),
    'model_api_url': fields.String(description='模型API地址'),
    'model_api_key': fields.String(description='模型API密钥'),
    'model_temperature': fields.Float(description='温度参数'),
    'model_max_tokens': fields.Integer(description='最大tokens'),
    'model_top_p': fields.Float(description='Top-p参数'),
    'model_top_k': fields.Integer(description='Top-k参数'),
    'model_presence_penalty': fields.Float(description='存在惩罚'),
    'model_frequency_penalty': fields.Float(description='频率惩罚'),
    'model_stop_sequences': fields.List(fields.String, description='停止序列'),
    'model_context_window': fields.Integer(description='上下文窗口大小'),
    'model_system_prompt': fields.String(description='系统提示词')
})

# 更新智能体状态请求模型
update_status_model = api.model('UpdateStatus', {
    'status': fields.String(required=True, description='智能体状态', enum=['inactive', 'running', 'paused', 'stopped'])
})

# 发送消息请求模型
send_message_model = api.model('SendMessage', {
    'content': fields.String(required=True, description='消息内容')
})

# 聊天请求模型
chat_model = api.model('Chat', {
    'content': fields.String(required=True, description='消息内容'),
    'conversation_id': fields.String(description='会话ID（可选）')
})

# 配置数据库
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')

if DB_TYPE == 'mysql':
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'agent_platform')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """根路由"""
    return jsonify({'message': 'Agent Management Platform API', 'docs_url': '/docs'})

# 智能体管理接口
@ns_agents.route('/')
class AgentList(Resource):
    @ns_agents.doc('list_agents')
    @ns_agents.marshal_list_with(agent_model)
    def get(self):
        """获取智能体列表"""
        try:
            # 分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # 查询智能体
            agents = Agent.query.order_by(Agent.created_at.desc()).paginate(page=page, per_page=per_page)
            
            # 构建响应
            response = {
                'agents': [agent.to_dict() for agent in agents.items],
                'total': agents.total,
                'pages': agents.pages,
                'current_page': agents.page,
                'per_page': agents.per_page
            }
            
            return response, 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @ns_agents.doc('create_agent')
    @ns_agents.expect(create_agent_model)
    @ns_agents.marshal_with(agent_model, code=201)
    def post(self):
        """注册新智能体"""
        try:
            data = request.get_json()
            
            # 验证必填字段
            if not data or 'name' not in data:
                return jsonify({'error': 'Name is required'}), 400
            
            # 检查智能体是否已存在
            existing_agent = Agent.query.filter_by(name=data['name']).first()
            if existing_agent:
                return jsonify({'error': 'Agent already exists'}), 409
            
            # 创建新智能体
            agent = Agent(
                name=data['name'],
                description=data.get('description', ''),
                status=data.get('status', 'inactive'),
                model_name=data.get('model_name', 'llama2'),
                model_provider=data.get('model_provider', 'ollama'),
                model_api_url=data.get('model_api_url', 'http://localhost:11434/v1'),
                model_api_key=data.get('model_api_key'),
                model_temperature=data.get('model_temperature', 0.7),
                model_max_tokens=data.get('model_max_tokens', 2048),
                model_top_p=data.get('model_top_p', 0.9),
                model_top_k=data.get('model_top_k', 40),
                model_presence_penalty=data.get('model_presence_penalty', 0.0),
                model_frequency_penalty=data.get('model_frequency_penalty', 0.0),
                model_stop_sequences=','.join(data.get('model_stop_sequences', [])) if data.get('model_stop_sequences') else None,
                model_context_window=data.get('model_context_window', 4096),
                model_system_prompt=data.get('model_system_prompt')
            )
            
            # 添加到数据库
            db.session.add(agent)
            db.session.commit()
            
            # 添加日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Agent "{agent.name}" created with status "{agent.status}"' 
            )
            db.session.add(log)
            db.session.commit()
            
            return agent.to_dict(), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@ns_agents.route('/<int:agent_id>')
@ns_agents.response(404, 'Agent not found')
@ns_agents.param('agent_id', '智能体ID')
class AgentResource(Resource):
    @ns_agents.doc('get_agent')
    @ns_agents.marshal_with(agent_model)
    def get(self, agent_id):
        """获取单个智能体信息"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            return agent.to_dict(), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @ns_agents.doc('update_agent')
    @ns_agents.expect(update_agent_model)
    @ns_agents.marshal_with(agent_model)
    def put(self, agent_id):
        """更新智能体信息"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            data = request.get_json()
            
            # 更新字段
            if 'name' in data:
                agent.name = data['name']
            if 'description' in data:
                agent.description = data['description']
            if 'status' in data:
                # 验证状态值
                valid_statuses = ['inactive', 'running', 'paused', 'stopped']
                if data['status'] not in valid_statuses:
                    return jsonify({'error': f'Invalid status. Must be one of {valid_statuses}'}), 400
                agent.status = data['status']
            if 'model_name' in data:
                agent.model_name = data['model_name']
            if 'model_provider' in data:
                agent.model_provider = data['model_provider']
            if 'model_api_url' in data:
                agent.model_api_url = data['model_api_url']
            if 'model_api_key' in data:
                agent.model_api_key = data['model_api_key']
            if 'model_temperature' in data:
                agent.model_temperature = data['model_temperature']
            if 'model_max_tokens' in data:
                agent.model_max_tokens = data['model_max_tokens']
            if 'model_top_p' in data:
                agent.model_top_p = data['model_top_p']
            if 'model_top_k' in data:
                agent.model_top_k = data['model_top_k']
            if 'model_presence_penalty' in data:
                agent.model_presence_penalty = data['model_presence_penalty']
            if 'model_frequency_penalty' in data:
                agent.model_frequency_penalty = data['model_frequency_penalty']
            if 'model_stop_sequences' in data:
                agent.model_stop_sequences = ','.join(data['model_stop_sequences']) if data['model_stop_sequences'] else None
            if 'model_context_window' in data:
                agent.model_context_window = data['model_context_window']
            if 'model_system_prompt' in data:
                agent.model_system_prompt = data['model_system_prompt']
            
            # 提交更新
            db.session.commit()
            
            # 添加日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Agent "{agent.name}" updated'
            )
            db.session.add(log)
            db.session.commit()
            
            return agent.to_dict(), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @ns_agents.doc('delete_agent')
    @ns_agents.response(204, 'Agent deleted')
    def delete(self, agent_id):
        """删除智能体"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            
            # 添加日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Agent "{agent.name}" deleted'
            )
            db.session.add(log)
            db.session.commit()
            
            # 删除智能体
            db.session.delete(agent)
            db.session.commit()
            
            return '', 204
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@ns_agents.route('/<int:agent_id>/status')
@ns_agents.response(404, 'Agent not found')
@ns_agents.param('agent_id', '智能体ID')
class AgentStatus(Resource):
    @ns_agents.doc('update_agent_status')
    @ns_agents.expect(update_status_model)
    @ns_agents.marshal_with(agent_model)
    def post(self, agent_id):
        """更新智能体状态（启动、暂停、停止）"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            data = request.get_json()
            
            # 验证状态值
            if 'status' not in data:
                return jsonify({'error': 'Status is required'}), 400
                
            valid_statuses = ['inactive', 'running', 'paused', 'stopped']
            if data['status'] not in valid_statuses:
                return jsonify({'error': f'Invalid status. Must be one of {valid_statuses}'}), 400
            
            # 更新状态
            old_status = agent.status
            agent.status = data['status']
            db.session.commit()
            
            # 添加日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Agent "{agent.name}" status changed from "{old_status}" to "{agent.status}"' 
            )
            db.session.add(log)
            db.session.commit()
            
            return agent.to_dict(), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@ns_agents.route('/<int:agent_id>/chat')
@ns_agents.response(404, 'Agent not found')
@ns_agents.param('agent_id', '智能体ID')
class AgentChat(Resource):
    @ns_agents.doc('chat_with_agent')
    @ns_agents.expect(chat_model)
    def post(self, agent_id):
        """直接与智能体对话（自动管理会话）"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            
            data = request.get_json()
            if not data or 'content' not in data:
                return jsonify({'error': 'Content is required'}), 400
            
            # 获取或创建会话
            conversation_id = data.get('conversation_id')
            if conversation_id:
                conversation = Conversation.query.filter_by(agent_id=agent.id, conversation_id=conversation_id).first()
                if not conversation:
                    return jsonify({'error': 'Conversation not found'}), 404
            else:
                # 创建新会话
                conversation_id = str(uuid.uuid4())
                conversation = Conversation(
                    agent_id=agent.id,
                    conversation_id=conversation_id
                )
                db.session.add(conversation)
                db.session.commit()
                
                # 添加日志
                log = AgentLog(
                    agent_id=agent.id,
                    level='info',
                    message=f'Conversation "{conversation_id}" created for agent "{agent.name}" via chat API' 
                )
                db.session.add(log)
                db.session.commit()
            
            # 添加用户消息
            user_message = Message(
                conversation_id=conversation.id,
                role='user',
                content=data['content']
            )
            db.session.add(user_message)
            db.session.commit()
            
            # 获取会话历史
            messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at).all()
            
            # 如果有系统提示词，确保它是第一条消息
            if agent.model_system_prompt:
                # 检查是否已经有系统消息
                has_system_message = any(msg.role == 'system' for msg in messages)
                if not has_system_message:
                    # 在消息列表开头插入系统提示词
                    system_message = Message(
                        conversation_id=conversation.id,
                        role='system',
                        content=agent.model_system_prompt
                    )
                    db.session.add(system_message)
                    db.session.commit()
                    # 重新获取消息列表
                    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at).all()
            
            # 构建请求参数
            request_data = {
                'model': agent.model_name,
                'messages': [{'role': msg.role, 'content': msg.content} for msg in messages],
                'temperature': agent.model_temperature,
                'max_tokens': agent.model_max_tokens,
                'top_p': agent.model_top_p,
                'top_k': agent.model_top_k,
                'presence_penalty': agent.model_presence_penalty,
                'frequency_penalty': agent.model_frequency_penalty
            }
            
            # 添加停止序列（如果有的话）
            if agent.model_stop_sequences:
                request_data['stop'] = agent.model_stop_sequences.split(',')
            
            # 发送请求到模型API
            headers = {
                'Content-Type': 'application/json'
            }
            if agent.model_provider == 'openai' and agent.model_api_key:
                headers['Authorization'] = f'Bearer {agent.model_api_key}'
            
            response = requests.post(f'{agent.model_api_url}/chat/completions', json=request_data, headers=headers)
            response.raise_for_status()
            
            # 解析模型响应
            response_data = response.json()
            assistant_message_content = response_data['choices'][0]['message']['content']
            
            # 添加助手消息
            assistant_message = Message(
                conversation_id=conversation.id,
                role='assistant',
                content=assistant_message_content
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            # 添加日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Message exchanged in conversation "{conversation_id}" for agent "{agent.name}" via chat API' 
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'message': 'Message sent successfully',
                'response': assistant_message_content,
                'conversation_id': conversation_id
            }), 200
            
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Model API error: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@ns_agents.route('/<int:agent_id>/logs')
@ns_agents.response(404, 'Agent not found')
@ns_agents.param('agent_id', '智能体ID')
class AgentLogs(Resource):
    @ns_agents.doc('get_agent_logs')
    @ns_agents.marshal_list_with(log_model)
    def get(self, agent_id):
        """获取智能体日志"""
        try:
            # 验证智能体是否存在
            agent = Agent.query.get_or_404(agent_id)
            
            # 分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            # 查询日志
            logs = AgentLog.query.filter_by(agent_id=agent_id).order_by(AgentLog.created_at.desc()).paginate(page=page, per_page=per_page)
            
            # 构建响应
            response = {
                'logs': [log.to_dict() for log in logs.items],
                'total': logs.total,
                'pages': logs.pages,
                'current_page': logs.page,
                'per_page': logs.per_page
            }
            
            return response, 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# 会话管理接口
@ns_conversations.route('/agents/<int:agent_id>/conversations')
@ns_conversations.response(404, 'Agent not found')
@ns_conversations.param('agent_id', '智能体ID')
class ConversationList(Resource):
    @ns_conversations.doc('create_conversation')
    @ns_conversations.marshal_with(conversation_model, code=201)
    def post(self, agent_id):
        """创建新会话"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            
            # 生成唯一会话ID
            conversation_id = str(uuid.uuid4())
            
            # 创建新会话
            conversation = Conversation(
                agent_id=agent.id,
                conversation_id=conversation_id
            )
            
            db.session.add(conversation)
            db.session.commit()
            
            # 添加日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Conversation "{conversation_id}" created for agent "{agent.name}"' 
            )
            db.session.add(log)
            db.session.commit()
            
            return conversation.to_dict(), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@ns_conversations.route('/agents/<int:agent_id>/conversations/<string:conversation_id>/messages')
@ns_conversations.response(404, 'Agent or Conversation not found')
@ns_conversations.param('agent_id', '智能体ID')
@ns_conversations.param('conversation_id', '会话ID')
class MessageList(Resource):
    @ns_conversations.doc('send_message')
    @ns_conversations.expect(send_message_model)
    def post(self, agent_id, conversation_id):
        """发送消息并获取智能体响应"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            conversation = Conversation.query.filter_by(agent_id=agent.id, conversation_id=conversation_id).first_or_404()
            
            data = request.get_json()
            if not data or 'content' not in data:
                return jsonify({'error': 'Content is required'}), 400
            
            # 添加用户消息
            user_message = Message(
                conversation_id=conversation.id,
                role='user',
                content=data['content']
            )
            db.session.add(user_message)
            db.session.commit()
            
            # 获取会话历史
            messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at).all()
            
            # 构建请求参数
            request_data = {
                'model': agent.model_name,
                'messages': [{'role': msg.role, 'content': msg.content} for msg in messages],
                'temperature': agent.model_temperature,
                'max_tokens': agent.model_max_tokens,
                'top_p': agent.model_top_p,
                'top_k': agent.model_top_k,
                'presence_penalty': agent.model_presence_penalty,
                'frequency_penalty': agent.model_frequency_penalty
            }
            
            # 添加停止序列（如果有的话）
            if agent.model_stop_sequences:
                request_data['stop'] = agent.model_stop_sequences.split(',')
            
            # 发送请求到模型API
            headers = {
                'Content-Type': 'application/json'
            }
            if agent.model_provider == 'openai' and agent.model_api_key:
                headers['Authorization'] = f'Bearer {agent.model_api_key}'
            
            response = requests.post(f'{agent.model_api_url}/chat/completions', json=request_data, headers=headers)
            response.raise_for_status()
            
            # 解析模型响应
            response_data = response.json()
            assistant_message_content = response_data['choices'][0]['message']['content']
            
            # 添加助手消息
            assistant_message = Message(
                conversation_id=conversation.id,
                role='assistant',
                content=assistant_message_content
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            # 添加日志
            log = AgentLog(
                agent_id=agent.id,
                level='info',
                message=f'Message exchanged in conversation "{conversation_id}" for agent "{agent.name}"' 
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({'message': 'Message sent successfully', 'response': assistant_message_content}), 200
            
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Model API error: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @ns_conversations.doc('get_conversation_messages')
    @ns_conversations.marshal_list_with(message_model)
    def get(self, agent_id, conversation_id):
        """获取会话历史消息"""
        try:
            agent = Agent.query.get_or_404(agent_id)
            conversation = Conversation.query.filter_by(agent_id=agent.id, conversation_id=conversation_id).first_or_404()
            
            # 获取会话历史
            messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at).all()
            
            return [msg.to_dict() for msg in messages], 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# 日志管理接口
@ns_logs.route('/')
class LogList(Resource):
    @ns_logs.doc('get_all_logs')
    @ns_logs.marshal_list_with(log_model)
    def get(self):
        """获取所有智能体日志"""
        try:
            # 分页参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            # 查询日志
            logs = AgentLog.query.order_by(AgentLog.created_at.desc()).paginate(page=page, per_page=per_page)
            
            # 构建响应
            response = {
                'logs': [log.to_dict() for log in logs.items],
                'total': logs.total,
                'pages': logs.pages,
                'current_page': logs.page,
                'per_page': logs.per_page
            }
            
            return response, 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)