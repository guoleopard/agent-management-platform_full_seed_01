# 智能体管理平台使用说明

## 项目简介

本项目是一个轻量级的智能体管理平台，提供智能体注册、列表查询、状态管理和日志查看等功能。

## 技术栈

- **后端框架**: Flask
- **数据库**: SQLite
- **ORM**: SQLAlchemy

## 安装步骤

### 1. 创建虚拟环境

```bash
# 使用 Python 3 内置的 venv 模块创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows 系统
venv\Scripts\activate
# macOS/Linux 系统
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行项目

```bash
python app.py
```

项目将在 `http://localhost:5000` 启动。

## API 接口文档

### 1. 注册智能体

**接口地址**: `POST /agents`

**请求示例**:
```json
{
  "name": "test-agent",
  "description": "测试智能体",
  "status": "inactive"
}
```

**响应示例**:
```json
{
  "message": "Agent created successfully",
  "agent": {
    "id": 1,
    "name": "test-agent",
    "description": "测试智能体",
    "status": "inactive",
    "created_at": "2023-06-15T10:00:00",
    "updated_at": "2023-06-15T10:00:00"
  }
}
```

### 2. 获取智能体列表

**接口地址**: `GET /agents`

**查询参数**:
- `page`: 页码（默认: 1）
- `per_page`: 每页数量（默认: 10）

**响应示例**:
```json
{
  "agents": [
    {
      "id": 1,
      "name": "test-agent",
      "description": "测试智能体",
      "status": "inactive",
      "created_at": "2023-06-15T10:00:00",
      "updated_at": "2023-06-15T10:00:00"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 10
}
```

### 3. 获取单个智能体信息

**接口地址**: `GET /agents/{agent_id}`

**响应示例**:
```json
{
  "agent": {
    "id": 1,
    "name": "test-agent",
    "description": "测试智能体",
    "status": "inactive",
    "created_at": "2023-06-15T10:00:00",
    "updated_at": "2023-06-15T10:00:00"
  }
}
```

### 4. 更新智能体信息

**接口地址**: `PUT /agents/{agent_id}`

**请求示例**:
```json
{
  "name": "updated-agent",
  "description": "更新后的测试智能体",
  "status": "running"
}
```

**响应示例**:
```json
{
  "message": "Agent updated successfully",
  "agent": {
    "id": 1,
    "name": "updated-agent",
    "description": "更新后的测试智能体",
    "status": "running",
    "created_at": "2023-06-15T10:00:00",
    "updated_at": "2023-06-15T10:30:00"
  }
}
```

### 5. 更新智能体状态

**接口地址**: `POST /agents/{agent_id}/status`

**请求示例**:
```json
{
  "status": "running"
}
```

**响应示例**:
```json
{
  "message": "Agent status updated successfully",
  "agent": {
    "id": 1,
    "name": "test-agent",
    "description": "测试智能体",
    "status": "running",
    "created_at": "2023-06-15T10:00:00",
    "updated_at": "2023-06-15T10:15:00"
  }
}
```

### 6. 获取智能体日志

**接口地址**: `GET /agents/{agent_id}/logs`

**查询参数**:
- `page`: 页码（默认: 1）
- `per_page`: 每页数量（默认: 20）

**响应示例**:
```json
{
  "logs": [
    {
      "id": 1,
      "agent_id": 1,
      "level": "info",
      "message": "Agent "test-agent" created with status "inactive"",
      "created_at": "2023-06-15T10:00:00"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 20
}
```

### 7. 获取所有日志

**接口地址**: `GET /logs`

**查询参数**:
- `page`: 页码（默认: 1）
- `per_page`: 每页数量（默认: 20）

**响应示例**:
```json
{
  "logs": [
    {
      "id": 1,
      "agent_id": 1,
      "level": "info",
      "message": "Agent "test-agent" created with status "inactive"",
      "created_at": "2023-06-15T10:00:00"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 20
}
```

### 8. 删除智能体

**接口地址**: `DELETE /agents/{agent_id}`

**响应示例**:
```json
{
  "message": "Agent deleted successfully"
}
```

## 状态说明

智能体支持以下状态:
- `inactive`: 未激活
- `running`: 运行中
- `paused`: 已暂停
- `stopped`: 已停止

## 日志级别

日志支持以下级别:
- `info`: 信息
- `warning`: 警告
- `error`: 错误
- `debug`: 调试
