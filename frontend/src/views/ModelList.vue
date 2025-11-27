<template>
  <div class="model-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>模型管理</h2>
      <el-button type="primary" @click="handleAddModel">
        <el-icon><Plus /></el-icon>
        添加模型
      </el-button>
    </div>

    <!-- 模型列表 -->
    <el-card class="model-list-card">
      <div class="model-list">
        <el-empty v-if="models.length === 0" description="暂无模型，请添加第一个模型吧" />
        <el-row :gutter="20" v-else>
          <el-col :span="6" v-for="model in models" :key="model.id">
            <el-card :body-style="{ padding: '15px' }" class="model-item">
              <div class="model-header">
                <h4>{{ model.name }}</h4>
                <el-tag :type="getProviderTagType(model.provider)">
                  {{ getProviderText(model.provider) }}
                </el-tag>
              </div>
              <p class="model-description">{{ model.description || '暂无描述' }}</p>
              <div class="model-meta">
                <span class="model-name">{{ model.model_name }}</span>
                <span class="create-time">{{ formatTime(model.created_at) }}</span>
              </div>
              <div class="model-actions">
                <el-button size="small" @click="handleEditModel(model)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button size="small" type="danger" @click="handleDeleteModel(model.id)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 模型表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingModel.id ? '编辑模型' : '添加模型'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="modelForm"
        :rules="rules"
        label-width="120px"
        class="model-form"
      >
        <el-form-item label="模型名称" prop="name">
          <el-input
            v-model="modelForm.name"
            placeholder="请输入模型名称"
          />
        </el-form-item>

        <el-form-item label="模型描述" prop="description">
          <el-input
            v-model="modelForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述"
          />
        </el-form-item>

        <el-form-item label="模型提供商" prop="provider">
          <el-select
            v-model="modelForm.provider"
            placeholder="请选择模型提供商"
          >
            <el-option label="Ollama" value="ollama" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Google" value="google" />
          </el-select>
        </el-form-item>

        <el-form-item label="模型标识" prop="model_name">
          <el-input
            v-model="modelForm.model_name"
            placeholder="请输入模型标识（如：llama2）"
          />
        </el-form-item>

        <el-form-item label="模型API地址" prop="api_url">
          <el-input
            v-model="modelForm.api_url"
            placeholder="请输入模型API地址"
          />
        </el-form-item>

        <el-form-item label="模型API密钥" prop="api_key">
          <el-input
            v-model="modelForm.api_key"
            type="password"
            placeholder="请输入模型API密钥（OpenAI等需要）"
            show-password
          />
        </el-form-item>

        <el-form-item label="温度参数" prop="temperature">
          <el-slider
            v-model="modelForm.temperature"
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
            v-model="modelForm.max_tokens"
            :min="128"
            :max="8192"
            :step="128"
            style="width: 100%"
          />
          <div class="form-tip">模型生成的最大文本长度</div>
        </el-form-item>

        <el-form-item label="Top-p参数" prop="top_p">
          <el-slider
            v-model="modelForm.top_p"
            :min="0"
            :max="1"
            :step="0.01"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制核采样的概率阈值</div>
        </el-form-item>

        <el-form-item label="Top-k参数" prop="top_k">
          <el-input-number
            v-model="modelForm.top_k"
            :min="1"
            :max="100"
            :step="1"
            style="width: 100%"
          />
          <div class="form-tip">限制每次采样的候选词数量</div>
        </el-form-item>

        <el-form-item label="存在惩罚" prop="presence_penalty">
          <el-slider
            v-model="modelForm.presence_penalty"
            :min="-2"
            :max="2"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制新主题的引入概率</div>
        </el-form-item>

        <el-form-item label="频率惩罚" prop="frequency_penalty">
          <el-slider
            v-model="modelForm.frequency_penalty"
            :min="-2"
            :max="2"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制重复内容的生成概率</div>
        </el-form-item>

        <el-form-item label="上下文窗口" prop="context_window">
          <el-input-number
            v-model="modelForm.context_window"
            :min="512"
            :max="16384"
            :step="512"
            style="width: 100%"
          />
          <div class="form-tip">模型能够处理的最大上下文长度</div>
        </el-form-item>

        <el-form-item label="系统提示词" prop="system_prompt">
          <el-input
            v-model="modelForm.system_prompt"
            type="textarea"
            :rows="5"
            placeholder="请输入系统提示词，定义模型的行为和角色"
          />
        </el-form-item>

        <el-form-item label="停止序列">
          <el-tag
            v-for="(tag, index) in modelForm.stop_sequences"
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
        <el-button type="primary" @click="handleSaveModel" :loading="loading">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Check } from '@element-plus/icons-vue'

const formRef = ref(null)
const dialogVisible = ref(false)
const loading = ref(false)
const editingModel = ref({})
const newStopSequence = ref('')
const models = ref([])

// 表单数据
const modelForm = reactive({
  name: '',
  description: '',
  provider: 'ollama',
  model_name: 'llama2',
  api_url: 'http://localhost:11434/v1',
  api_key: '',
  temperature: 0.7,
  max_tokens: 2048,
  top_p: 0.9,
  top_k: 40,
  presence_penalty: 0.0,
  frequency_penalty: 0.0,
  context_window: 4096,
  system_prompt: '',
  stop_sequences: []
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 2, max: 100, message: '名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过 500 个字符', trigger: 'blur' }
  ],
  provider: [
    { required: true, message: '请选择模型提供商', trigger: 'change' }
  ],
  model_name: [
    { required: true, message: '请输入模型标识', trigger: 'blur' }
  ],
  api_url: [
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
  ],
  top_p: [
    { required: true, message: '请输入Top-p参数', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: 'Top-p参数必须在0到1之间', trigger: 'blur' }
  ],
  top_k: [
    { required: true, message: '请输入Top-k参数', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: 'Top-k参数必须在1到100之间', trigger: 'blur' }
  ],
  presence_penalty: [
    { required: true, message: '请输入存在惩罚', trigger: 'blur' },
    { type: 'number', min: -2, max: 2, message: '存在惩罚必须在-2到2之间', trigger: 'blur' }
  ],
  frequency_penalty: [
    { required: true, message: '请输入频率惩罚', trigger: 'blur' },
    { type: 'number', min: -2, max: 2, message: '频率惩罚必须在-2到2之间', trigger: 'blur' }
  ],
  context_window: [
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
  if (newStopSequence.value.trim() && !modelForm.stop_sequences.includes(newStopSequence.value.trim())) {
    modelForm.stop_sequences.push(newStopSequence.value.trim())
    newStopSequence.value = ''
  }
}

// 移除停止序列
const handleTagClose = (index) => {
  modelForm.stop_sequences.splice(index, 1)
}

// 添加模型
const handleAddModel = () => {
  editingModel.value = {}
  resetForm()
  dialogVisible.value = true
}

// 编辑模型
const handleEditModel = (model) => {
  editingModel.value = { ...model }
  Object.assign(modelForm, {
    name: model.name,
    description: model.description || '',
    provider: model.provider,
    model_name: model.model_name,
    api_url: model.api_url,
    api_key: model.api_key || '',
    temperature: model.temperature,
    max_tokens: model.max_tokens,
    top_p: model.top_p,
    top_k: model.top_k,
    presence_penalty: model.presence_penalty,
    frequency_penalty: model.frequency_penalty,
    context_window: model.context_window,
    system_prompt: model.system_prompt || '',
    stop_sequences: model.stop_sequences || []
  })
  dialogVisible.value = true
}

// 保存模型
const handleSaveModel = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const modelData = { ...modelForm }
    
    if (editingModel.value.id) {
      // 编辑模式
      await $axios.put(`/models/${editingModel.value.id}`, modelData)
      ElMessage.success('模型更新成功')
    } else {
      // 创建模式
      await $axios.post('/models/', modelData)
      ElMessage.success('模型创建成功')
    }
    
    dialogVisible.value = false
    loadModels()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(editingModel.value.id ? '更新失败' : '创建失败')
  } finally {
    loading.value = false
  }
}

// 删除模型
const handleDeleteModel = async (modelId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模型吗？', '确认删除', {
      type: 'warning'
    })
    
    await $axios.delete(`/models/${modelId}`)
    ElMessage.success('模型删除成功')
    loadModels()
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
  editingModel.value = {}
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  modelForm.stop_sequences = []
  newStopSequence.value = ''
}

// 获取提供商标签类型
const getProviderTagType = (provider) => {
  const providerMap = {
    'ollama': 'info',
    'openai': 'success',
    'anthropic': 'warning',
    'google': 'danger'
  }
  return providerMap[provider] || 'info'
}

// 获取提供商文本
const getProviderText = (provider) => {
  const providerMap = {
    'ollama': 'Ollama',
    'openai': 'OpenAI',
    'anthropic': 'Anthropic',
    'google': 'Google'
  }
  return providerMap[provider] || provider
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

// 加载模型列表
const loadModels = async () => {
  try {
    const response = await $axios.get('/models/')
    models.value = response.data.models || []
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  }
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.model-list-container {
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

.model-list-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.model-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.model-item {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.model-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.model-description {
  margin: 10px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  flex: 1;
}

.model-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 12px;
  color: #999;
}

.model-actions {
  display: flex;
  gap: 5px;
  justify-content: flex-end;
}

.model-form {
  padding: 20px 0;
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}
</style>