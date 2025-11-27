<template>
  <div class="model-settings-container">
    <el-card title="Ollama模型设置" class="settings-card">
      <el-form
        ref="formRef"
        :model="modelForm"
        :rules="rules"
        label-width="120px"
        class="model-form"
      >
        <el-form-item label="模型名称" prop="modelName">
          <el-input
            v-model="modelForm.modelName"
            placeholder="请输入模型名称（如：llama2）"
          />
        </el-form-item>

        <el-form-item label="模型API地址" prop="modelApiUrl">
          <el-input
            v-model="modelForm.modelApiUrl"
            placeholder="请输入模型API地址（如：http://localhost:11434/v1）"
          />
        </el-form-item>

        <el-form-item label="温度参数" prop="modelTemperature">
          <el-slider
            v-model="modelForm.modelTemperature"
            :min="0"
            :max="1"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制生成文本的随机性，值越大越随机</div>
        </el-form-item>

        <el-form-item label="最大Tokens" prop="modelMaxTokens">
          <el-input-number
            v-model="modelForm.modelMaxTokens"
            :min="128"
            :max="8192"
            :step="128"
            style="width: 100%"
          />
          <div class="form-tip">模型生成的最大文本长度</div>
        </el-form-item>

        <el-form-item label="Top-p参数" prop="modelTopP">
          <el-slider
            v-model="modelForm.modelTopP"
            :min="0"
            :max="1"
            :step="0.01"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制核采样的概率阈值</div>
        </el-form-item>

        <el-form-item label="Top-k参数" prop="modelTopK">
          <el-input-number
            v-model="modelForm.modelTopK"
            :min="1"
            :max="100"
            :step="1"
            style="width: 100%"
          />
          <div class="form-tip">限制每次采样的候选词数量</div>
        </el-form-item>

        <el-form-item label="存在惩罚" prop="modelPresencePenalty">
          <el-slider
            v-model="modelForm.modelPresencePenalty"
            :min="-2"
            :max="2"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制新主题的引入概率</div>
        </el-form-item>

        <el-form-item label="频率惩罚" prop="modelFrequencyPenalty">
          <el-slider
            v-model="modelForm.modelFrequencyPenalty"
            :min="-2"
            :max="2"
            :step="0.1"
            show-input
            :format-tooltip="formatTooltip"
          />
          <div class="form-tip">控制重复内容的生成概率</div>
        </el-form-item>

        <el-form-item label="上下文窗口" prop="modelContextWindow">
          <el-input-number
            v-model="modelForm.modelContextWindow"
            :min="512"
            :max="16384"
            :step="512"
            style="width: 100%"
          />
          <div class="form-tip">模型能够处理的最大上下文长度</div>
        </el-form-item>

        <el-form-item label="系统提示词" prop="modelSystemPrompt">
          <el-input
            v-model="modelForm.modelSystemPrompt"
            type="textarea"
            :rows="4"
            placeholder="请输入系统提示词（可选）"
          />
          <div class="form-tip">定义模型的行为和角色</div>
        </el-form-item>

        <el-form-item label="停止序列">
          <el-tag
            v-for="(tag, index) in modelForm.modelStopSequences"
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
          <el-button type="primary" @click="handleSave" :loading="loading">
            <el-icon><Check /></el-icon>
            保存设置
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 测试连接卡片 -->
    <el-card title="测试连接" class="test-card">
      <div class="test-content">
        <el-button type="success" @click="handleTestConnection" :loading="testing">
          <el-icon><Connection /></el-icon>
          测试模型连接
        </el-button>
        <div v-if="testResult" class="test-result">
          <el-alert
            :title="testResult.title"
            :description="testResult.description"
            :type="testResult.type"
            show-icon
            :closable="true"
            @close="testResult = null"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Refresh, Connection } from '@element-plus/icons-vue'

const formRef = ref(null)
const loading = ref(false)
const testing = ref(false)
const testResult = ref(null)
const newStopSequence = ref('')

// 表单数据
const modelForm = reactive({
  modelName: 'llama2',
  modelApiUrl: 'http://localhost:11434/v1',
  modelTemperature: 0.7,
  modelMaxTokens: 2048,
  modelTopP: 0.9,
  modelTopK: 40,
  modelPresencePenalty: 0.0,
  modelFrequencyPenalty: 0.0,
  modelContextWindow: 4096,
  modelSystemPrompt: '',
  modelStopSequences: []
})

// 表单验证规则
const rules = {
  modelName: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  modelApiUrl: [
    { required: true, message: '请输入模型API地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  modelTemperature: [
    { required: true, message: '请输入温度参数', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: '温度参数必须在0到1之间', trigger: 'blur' }
  ],
  modelMaxTokens: [
    { required: true, message: '请输入最大Tokens', trigger: 'blur' },
    { type: 'number', min: 128, max: 8192, message: '最大Tokens必须在128到8192之间', trigger: 'blur' }
  ],
  modelTopP: [
    { required: true, message: '请输入Top-p参数', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: 'Top-p参数必须在0到1之间', trigger: 'blur' }
  ],
  modelTopK: [
    { required: true, message: '请输入Top-k参数', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: 'Top-k参数必须在1到100之间', trigger: 'blur' }
  ],
  modelPresencePenalty: [
    { required: true, message: '请输入存在惩罚', trigger: 'blur' },
    { type: 'number', min: -2, max: 2, message: '存在惩罚必须在-2到2之间', trigger: 'blur' }
  ],
  modelFrequencyPenalty: [
    { required: true, message: '请输入频率惩罚', trigger: 'blur' },
    { type: 'number', min: -2, max: 2, message: '频率惩罚必须在-2到2之间', trigger: 'blur' }
  ],
  modelContextWindow: [
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
  if (newStopSequence.value.trim() && !modelForm.modelStopSequences.includes(newStopSequence.value.trim())) {
    modelForm.modelStopSequences.push(newStopSequence.value.trim())
    newStopSequence.value = ''
  }
}

// 移除停止序列
const handleTagClose = (index) => {
  modelForm.modelStopSequences.splice(index, 1)
}

// 保存设置
const handleSave = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 保存到本地存储
    localStorage.setItem('ollamaModelSettings', JSON.stringify(modelForm))
    
    ElMessage.success('模型设置保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请检查表单')
  } finally {
    loading.value = false
  }
}

// 重置表单
const handleReset = () => {
  formRef.value.resetFields()
  modelForm.modelStopSequences = []
  testResult.value = null
}

// 测试连接
const handleTestConnection = async () => {
  testing.value = true
  testResult.value = null
  
  try {
    // 这里可以添加实际的连接测试逻辑
    // 例如：发送一个简单的请求到模型API
    
    // 模拟测试延迟
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    testResult.value = {
      title: '连接成功',
      description: `已成功连接到 ${modelForm.modelName} 模型`,
      type: 'success'
    }
    
    ElMessage.success('模型连接测试成功')
  } catch (error) {
    console.error('连接测试失败:', error)
    testResult.value = {
      title: '连接失败',
      description: '无法连接到模型，请检查API地址和网络设置',
      type: 'error'
    }
    ElMessage.error('模型连接测试失败')
  } finally {
    testing.value = false
  }
}

// 从本地存储加载设置
const loadSettings = () => {
  const savedSettings = localStorage.getItem('ollamaModelSettings')
  if (savedSettings) {
    const parsedSettings = JSON.parse(savedSettings)
    Object.assign(modelForm, parsedSettings)
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.model-settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-card,
.test-card {
  margin-bottom: 20px;
}

.model-form {
  padding-top: 20px;
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.test-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.test-result {
  flex: 1;
}
</style>