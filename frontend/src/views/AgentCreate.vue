<template>
  <div class="agent-create-container">
    <el-card title="创建智能体" class="create-card">
      <el-form
        ref="formRef"
        :model="agentForm"
        :rules="rules"
        label-width="120px"
        class="agent-form"
      >
        <el-form-item label="智能体名称" prop="name">
          <el-input
            v-model="agentForm.name"
            placeholder="请输入智能体名称"
          />
        </el-form-item>

        <el-form-item label="智能体描述" prop="description">
          <el-input
            v-model="agentForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入智能体描述"
          />
        </el-form-item>

        <el-form-item label="智能体状态" prop="status">
          <el-select
            v-model="agentForm.status"
            placeholder="请选择智能体状态"
          >
            <el-option label="未激活" value="inactive" />
            <el-option label="运行中" value="running" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已停止" value="stopped" />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">模型配置</el-divider>

        <el-form-item label="模型名称" prop="model_name">
          <el-input
            v-model="agentForm.model_name"
            placeholder="请输入模型名称（如：llama2）"
          />
        </el-form-item>

        <el-form-item label="模型提供商" prop="model_provider">
          <el-select
            v-model="agentForm.model_provider"
            placeholder="请选择模型提供商"
          >
            <el-option label="Ollama" value="ollama" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Google" value="google" />
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

        <el-form-item label="温度参数" prop="model_temperature">
          <el-slider
            v-model="agentForm.model_temperature"
            :min="0"
            :max="1"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制生成文本的随机性，值越大越随机</div>
        </el-form-item>

        <el-form-item label="最大Tokens" prop="model_max_tokens">
          <el-input-number
            v-model="agentForm.model_max_tokens"
            :min="128"
            :max="8192"
            :step="128"
            style="width: 100%"
          />
          <div class="form-tip">模型生成的最大文本长度</div>
        </el-form-item>

        <el-form-item label="Top-p参数" prop="model_top_p">
          <el-slider
            v-model="agentForm.model_top_p"
            :min="0"
            :max="1"
            :step="0.01"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制核采样的概率阈值</div>
        </el-form-item>

        <el-form-item label="Top-k参数" prop="model_top_k">
          <el-input-number
            v-model="agentForm.model_top_k"
            :min="1"
            :max="100"
            :step="1"
            style="width: 100%"
          />
          <div class="form-tip">限制每次采样的候选词数量</div>
        </el-form-item>

        <el-form-item label="存在惩罚" prop="model_presence_penalty">
          <el-slider
            v-model="agentForm.model_presence_penalty"
            :min="-2"
            :max="2"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制新主题的引入概率</div>
        </el-form-item>

        <el-form-item label="频率惩罚" prop="model_frequency_penalty">
          <el-slider
            v-model="agentForm.model_frequency_penalty"
            :min="-2"
            :max="2"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制重复内容的生成概率</div>
        </el-form-item>

        <el-form-item label="上下文窗口" prop="model_context_window">
          <el-input-number
            v-model="agentForm.model_context_window"
            :min="512"
            :max="16384"
            :step="512"
            style="width: 100%"
          />
          <div class="form-tip">模型能够处理的最大上下文长度</div>
        </el-form-item>

        <el-form-item label="系统提示词" prop="model_system_prompt">
          <el-input
            v-model="agentForm.model_system_prompt"
            type="textarea"
            :rows="5"
            placeholder="请输入系统提示词，定义智能体的行为和角色"
          />
          <div class="form-tip">例如：你是一个 helpful、harmless、honest 的AI助手</div>
        </el-form-item>

        <el-form-item label="停止序列">
          <el-tag
            v-for="(tag, index) in agentForm.model_stop_sequences"
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

        <el-form-item>
          <el-button type="primary" @click="handleCreate" :loading="loading">
            <el-icon><Plus /></el-icon>
            创建智能体
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button @click="handleLoadModelSettings">
            <el-icon><Setting /></el-icon>
            加载模型设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 智能体列表卡片 -->
    <el-card title="智能体列表" class="list-card">
      <div class="agent-list">
        <el-empty v-if="agents.length === 0" description="暂无智能体，请创建第一个智能体吧" />
        <el-row :gutter="20" v-else>
          <el-col :span="8" v-for="agent in agents" :key="agent.id">
            <el-card :body-style="{ padding: '15px' }" class="agent-item">
              <div class="agent-header">
                <h4>{{ agent.name }}</h4>
                <el-tag :type="getStatusTagType(agent.status)">
                  {{ getStatusText(agent.status) }}
                </el-tag>
              </div>
              <p class="agent-description">{{ agent.description || '暂无描述' }}</p>
              <div class="agent-meta">
                <span class="model-info">{{ agent.model_name }}</span>
                <span class="create-time">{{ formatTime(agent.created_at) }}</span>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Setting, Edit, Delete } from '@element-plus/icons-vue'

const formRef = ref(null)
const loading = ref(false)
const editingAgentId = ref(null)
const newStopSequence = ref('')
const agents = ref([])

// 表单数据
const agentForm = reactive({
  name: '',
  description: '',
  status: 'inactive',
  model_name: 'llama2',
  model_provider: 'ollama',
  model_api_url: 'http://localhost:11434/v1',
  model_api_key: '',
  model_temperature: 0.7,
  model_max_tokens: 2048,
  model_top_p: 0.9,
  model_top_k: 40,
  model_presence_penalty: 0.0,
  model_frequency_penalty: 0.0,
  model_context_window: 4096,
  model_system_prompt: '',
  model_stop_sequences: []
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入智能体名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过 500 个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择智能体状态', trigger: 'change' }
  ],
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  model_provider: [
    { required: true, message: '请选择模型提供商', trigger: 'change' }
  ],
  model_api_url: [
    { required: true, message: '请输入模型API地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  model_temperature: [
    { required: true, message: '请输入温度参数', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: '温度参数必须在0到1之间', trigger: 'blur' }
  ],
  model_max_tokens: [
    { required: true, message: '请输入最大Tokens', trigger: 'blur' },
    { type: 'number', min: 128, max: 8192, message: '最大Tokens必须在128到8192之间', trigger: 'blur' }
  ],
  model_top_p: [
    { required: true, message: '请输入Top-p参数', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: 'Top-p参数必须在0到1之间', trigger: 'blur' }
  ],
  model_top_k: [
    { required: true, message: '请输入Top-k参数', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: 'Top-k参数必须在1到100之间', trigger: 'blur' }
  ],
  model_presence_penalty: [
    { required: true, message: '请输入存在惩罚', trigger: 'blur' },
    { type: 'number', min: -2, max: 2, message: '存在惩罚必须在-2到2之间', trigger: 'blur' }
  ],
  model_frequency_penalty: [
    { required: true, message: '请输入频率惩罚', trigger: 'blur' },
    { type: 'number', min: -2, max: 2, message: '频率惩罚必须在-2到2之间', trigger: 'blur' }
  ],
  model_context_window: [
    { required: true, message: '请输入上下文窗口', trigger: 'blur' },
    { type: 'number', min: 512, max: 16384, message: '上下文窗口必须在512到16384之间', trigger: 'blur' }
  ]
}

// 格式化滑块提示
const formatTooltip = (value) => {
  return value.toString()
}

// 添加停止序列
const handleAddStopSequence = () => {
  if (newStopSequence.value.trim() && !agentForm.model_stop_sequences.includes(newStopSequence.value.trim())) {
    agentForm.model_stop_sequences.push(newStopSequence.value.trim())
    newStopSequence.value = ''
  }
}

// 移除停止序列
const handleTagClose = (index) => {
  agentForm.model_stop_sequences.splice(index, 1)
}

// 加载模型设置
const handleLoadModelSettings = () => {
  const savedSettings = localStorage.getItem('ollamaModelSettings')
  if (savedSettings) {
    const parsedSettings = JSON.parse(savedSettings)
    agentForm.model_name = parsedSettings.modelName
    agentForm.model_api_url = parsedSettings.modelApiUrl
    agentForm.model_temperature = parsedSettings.modelTemperature
    agentForm.model_max_tokens = parsedSettings.modelMaxTokens
    agentForm.model_top_p = parsedSettings.modelTopP
    agentForm.model_top_k = parsedSettings.modelTopK
    agentForm.model_presence_penalty = parsedSettings.modelPresencePenalty
    agentForm.model_frequency_penalty = parsedSettings.modelFrequencyPenalty
    agentForm.model_context_window = parsedSettings.modelContextWindow
    agentForm.model_system_prompt = parsedSettings.modelSystemPrompt
    agentForm.model_stop_sequences = parsedSettings.modelStopSequences || []
    ElMessage.success('模型设置已加载')
  } else {
    ElMessage.info('没有找到保存的模型设置')
  }
}

// 创建智能体
const handleCreate = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const agentData = { ...agentForm }
    
    if (editingAgentId.value) {
      // 编辑模式
      await $axios.put(`/agents/${editingAgentId.value}`, agentData)
      ElMessage.success('智能体更新成功')
      editingAgentId.value = null
    } else {
      // 创建模式
      await $axios.post('/agents/', agentData)
      ElMessage.success('智能体创建成功')
    }
    
    handleReset()
    loadAgents()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(editingAgentId.value ? '更新失败' : '创建失败')
  } finally {
    loading.value = false
  }
}

// 重置表单
const handleReset = () => {
  formRef.value.resetFields()
  agentForm.model_stop_sequences = []
  editingAgentId.value = null
}

// 编辑智能体
const handleEditAgent = (agent) => {
  editingAgentId.value = agent.id
  
  // 填充表单数据
  Object.assign(agentForm, {
    name: agent.name,
    description: agent.description,
    status: agent.status,
    model_name: agent.model_name,
    model_provider: agent.model_provider,
    model_api_url: agent.model_api_url,
    model_api_key: agent.model_api_key || '',
    model_temperature: agent.model_temperature,
    model_max_tokens: agent.model_max_tokens,
    model_top_p: agent.model_top_p,
    model_top_k: agent.model_top_k,
    model_presence_penalty: agent.model_presence_penalty,
    model_frequency_penalty: agent.model_frequency_penalty,
    model_context_window: agent.model_context_window,
    model_system_prompt: agent.model_system_prompt || '',
    model_stop_sequences: agent.model_stop_sequences || []
  })
  
  // 滚动到表单顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 删除智能体
const handleDeleteAgent = async (agentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个智能体吗？', '确认删除', {
      type: 'warning'
    })
    
    await $axios.delete(`/agents/${agentId}`)
    ElMessage.success('智能体删除成功')
    loadAgents()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const statusMap = {
    'inactive': 'info',
    'running': 'success',
    'paused': 'warning',
    'stopped': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'inactive': '未激活',
    'running': '运行中',
    'paused': '已暂停',
    'stopped': '已停止'
  }
  return statusMap[status] || status
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

// 加载智能体列表
const loadAgents = async () => {
  try {
    const response = await $axios.get('/agents/')
    agents.value = response.data.agents || []
  } catch (error) {
    console.error('加载智能体列表失败:', error)
    ElMessage.error('加载智能体列表失败')
  }
}

onMounted(() => {
  loadAgents()
})
</script>

<style scoped>
.agent-create-container {
  max-width: 1200px;
  margin: 0 auto;
}

.create-card,
.list-card {
  margin-bottom: 20px;
}

.agent-form {
  padding-top: 20px;
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.agent-list {
  min-height: 200px;
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
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 12px;
  color: #999;
}

.agent-actions {
  display: flex;
  gap: 5px;
  justify-content: flex-end;
}
</style>