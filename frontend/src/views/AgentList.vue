<template>
  <div class="agent-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>Agent管理</h2>
      <el-button type="primary" @click="handleAddAgent">
        <el-icon><Plus /></el-icon>
        添加Agent
      </el-button>
    </div>

    <!-- Agent列表 -->
    <el-card class="agent-list-card">
      <div class="agent-list">
        <el-empty v-if="agents.length === 0" description="暂无Agent，请添加第一个Agent吧" />
        <el-row :gutter="20" v-else>
          <el-col :span="8" v-for="agent in agents" :key="agent.id">
            <el-card :body-style="{ padding: '15px' }" class="agent-item">
              <div class="agent-header">
                <h4>{{ agent.name }}</h4>
                <el-tag :type="getAgentStatusTagType(agent.status)">
                  {{ getAgentStatusText(agent.status) }}
                </el-tag>
              </div>
              <p class="agent-description">{{ agent.description || '暂无描述' }}</p>
              <div class="agent-meta">
                <div class="model-info">
                  <el-icon size="14"><ChatDotRound /></el-icon>
                  <span>{{ agent.model_name || '未配置模型' }}</span>
                </div>
                <div class="create-time">{{ formatTime(agent.created_at) }}</div>
              </div>
              <div class="agent-actions">
                <el-button size="small" @click="handleEditAgent(agent)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button size="small" type="danger" @click="handleDeleteAgent(agent.id)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- Agent表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingAgent.id ? '编辑Agent' : '添加Agent'"
      width="700px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="agentForm"
        :rules="rules"
        label-width="120px"
        class="agent-form"
      >
        <el-form-item label="Agent名称" prop="name">
          <el-input
            v-model="agentForm.name"
            placeholder="请输入Agent名称"
          />
        </el-form-item>

        <el-form-item label="Agent描述" prop="description">
          <el-input
            v-model="agentForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入Agent描述"
          />
        </el-form-item>

        <el-form-item label="Agent状态" prop="status">
          <el-select
            v-model="agentForm.status"
            placeholder="请选择Agent状态"
          >
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>

        <el-divider />

        <el-form-item label="模型提供商" prop="model_provider">
          <el-select
            v-model="agentForm.model_provider"
            placeholder="请选择模型提供商"
            @change="handleModelProviderChange"
          >
            <el-option label="Ollama" value="ollama" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Google" value="google" />
          </el-select>
        </el-form-item>

        <el-form-item label="模型选择" prop="model_name">
          <el-select
            v-model="agentForm.model_name"
            placeholder="请选择模型"
            @change="handleModelChange"
          >
            <el-option
              v-for="model in availableModels"
              :key="model.model_name"
              :label="model.name"
              :value="model.model_name"
            >
              <span style="float: left">{{ model.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ model.provider }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="模型API地址" prop="model_api_url">
          <el-input
            v-model="agentForm.model_api_url"
            placeholder="请输入模型API地址"
          />
        </el-form-item>

        <el-form-item label="模型API密钥" prop="model_api_key">
          <el-input
            v-model="agentForm.model_api_key"
            type="password"
            placeholder="请输入模型API密钥（OpenAI等需要）"
            show-password
          />
        </el-form-item>

        <el-form-item label="温度参数" prop="temperature">
          <el-slider
            v-model="agentForm.temperature"
            :min="0"
            :max="1"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制生成文本的随机性，值越大越随机</div>
        </el-form-item>

        <el-form-item label="最大Tokens" prop="max_tokens">
          <el-input-number
            v-model="agentForm.max_tokens"
            :min="128"
            :max="8192"
            :step="128"
            style="width: 100%"
          />
          <div class="form-tip">模型生成的最大文本长度</div>
        </el-form-item>

        <el-form-item label="系统提示词" prop="system_prompt">
          <el-input
            v-model="agentForm.system_prompt"
            type="textarea"
            :rows="6"
            placeholder="请输入系统提示词，定义Agent的行为和角色"
          />
        </el-form-item>

        <el-form-item label="停止序列">
          <el-tag
            v-for="(tag, index) in agentForm.stop_sequences"
            :key="index"
            closable
            @close="handleTagClose(index)"
          >
            {{ tag }}
          </el-tag>
          <el-input
            v-model="newStopSequence"
            placeholder="输入后按回车添加"
            @keyup.enter="handleAddStopSequence"
            style="width: 200px; margin-left: 10px"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAgent" :loading="loading">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Check, ChatDotRound } from '@element-plus/icons-vue'

const formRef = ref(null)
const dialogVisible = ref(false)
const loading = ref(false)
const editingAgent = ref({})
const newStopSequence = ref('')
const agents = ref([])
const models = ref([])
const availableModels = ref([])

// 表单数据
const agentForm = reactive({
  name: '',
  description: '',
  status: 'active',
  model_provider: 'ollama',
  model_name: '',
  model_api_url: 'http://localhost:11434/v1',
  model_api_key: '',
  temperature: 0.7,
  max_tokens: 2048,
  system_prompt: '',
  stop_sequences: []
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入Agent名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过 500 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择Agent状态', trigger: 'change' }
  ],
  model_provider: [
    { required: true, message: '请选择模型提供商', trigger: 'change' }
  ],
  model_name: [
    { required: true, message: '请选择模型', trigger: 'change' }
  ],
  model_api_url: [
    { required: true, message: '请输入模型API地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  temperature: [
    { required: true, message: '请输入温度参数', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: '温度参数必须在0到1之间', trigger: 'blur' }
  ],
  max_tokens: [
    { required: true, message: '请输入最大Tokens', trigger: 'blur' },
    { type: 'number', min: 128, max: 8192, message: '最大Tokens必须在128到8192之间', trigger: 'blur' }
  ]
}

// 格式化滑块提示
const formatTooltip = (value) => {
  return value.toString()
}

// 添加停止序列
const handleAddStopSequence = () => {
  if (newStopSequence.value.trim() && !agentForm.stop_sequences.includes(newStopSequence.value.trim())) {
    agentForm.stop_sequences.push(newStopSequence.value.trim())
    newStopSequence.value = ''
  }
}

// 移除停止序列
const handleTagClose = (index) => {
  agentForm.stop_sequences.splice(index, 1)
}

// 模型提供商变化
const handleModelProviderChange = (provider) => {
  availableModels.value = models.value.filter(model => model.provider === provider)
  agentForm.model_name = ''
  agentForm.model_api_url = ''
  agentForm.model_api_key = ''
}

// 模型变化
const handleModelChange = (modelName) => {
  const selectedModel = models.value.find(model => model.model_name === modelName)
  if (selectedModel) {
    agentForm.model_api_url = selectedModel.api_url
    agentForm.model_api_key = selectedModel.api_key || ''
    agentForm.temperature = selectedModel.temperature
    agentForm.max_tokens = selectedModel.max_tokens
  }
}

// 添加Agent
const handleAddAgent = () => {
  editingAgent.value = {}
  resetForm()
  dialogVisible.value = true
}

// 编辑Agent
const handleEditAgent = (agent) => {
  editingAgent.value = { ...agent }
  Object.assign(agentForm, {
    name: agent.name,
    description: agent.description || '',
    status: agent.status,
    model_provider: agent.model_provider,
    model_name: agent.model_name,
    model_api_url: agent.model_api_url,
    model_api_key: agent.model_api_key || '',
    temperature: agent.temperature,
    max_tokens: agent.max_tokens,
    system_prompt: agent.system_prompt || '',
    stop_sequences: agent.stop_sequences || []
  })
  handleModelProviderChange(agent.model_provider)
  dialogVisible.value = true
}

// 保存Agent
const handleSaveAgent = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const agentData = { ...agentForm }
    
    if (editingAgent.value.id) {
      // 编辑模式
      await $axios.put(`/agents/${editingAgent.value.id}`, agentData)
      ElMessage.success('Agent更新成功')
    } else {
      // 创建模式
      await $axios.post('/agents/', agentData)
      ElMessage.success('Agent创建成功')
    }
    
    dialogVisible.value = false
    loadAgents()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(editingAgent.value.id ? '更新失败' : '创建失败')
  } finally {
    loading.value = false
  }
}

// 删除Agent
const handleDeleteAgent = async (agentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个Agent吗？', '确认删除', {
      type: 'warning'
    })
    
    await $axios.delete(`/agents/${agentId}`)
    ElMessage.success('Agent删除成功')
    loadAgents()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
  editingAgent.value = {}
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  agentForm.stop_sequences = []
  newStopSequence.value = ''
  handleModelProviderChange('ollama')
}

// 获取Agent状态标签类型
const getAgentStatusTagType = (status) => {
  return status === 'active' ? 'success' : 'danger'
}

// 获取Agent状态文本
const getAgentStatusText = (status) => {
  return status === 'active' ? '启用' : '禁用'
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

// 加载Agent列表
const loadAgents = async () => {
  try {
    const response = await $axios.get('/agents/')
    agents.value = response.data.agents || []
  } catch (error) {
    console.error('加载Agent列表失败:', error)
    ElMessage.error('加载Agent列表失败')
  }
}

// 加载模型列表
const loadModels = async () => {
  try {
    const response = await $axios.get('/models/')
    models.value = response.data.models || []
    availableModels.value = models.value.filter(model => model.provider === 'ollama')
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  }
}

onMounted(() => {
  loadAgents()
  loadModels()
})
</script>

<style scoped>
.agent-list-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.agent-list-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.agent-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.agent-item {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.agent-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.agent-description {
  margin: 10px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  flex: 1;
}

.agent-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 10px;
  font-size: 12px;
  color: #999;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.agent-actions {
  display: flex;
  gap: 5px;
  justify-content: flex-end;
}

.agent-form {
  padding: 20px 0;
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}
</style>