<template>
  <div class="role-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>角色管理</h2>
      <el-button type="primary" @click="handleAddRole">
        <el-icon><Plus /></el-icon>
        添加角色
      </el-button>
    </div>

    <!-- 角色列表 -->
    <el-card class="role-list-card">
      <div class="role-list">
        <el-table :data="roles" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="角色名称" />
          <el-table-column prop="description" label="角色描述" />
          <el-table-column prop="user_count" label="关联用户数" width="120" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column prop="updated_at" label="更新时间" width="180" />
          <el-table-column label="操作" width="300" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEditRole(scope.row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" @click="handleAssignUsers(scope.row)">
                <el-icon><User /></el-icon>
                分配用户
              </el-button>
              <el-button size="small" type="danger" @click="handleDeleteRole(scope.row.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 角色表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingRole.id ? '编辑角色' : '添加角色'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="roleForm"
        :rules="rules"
        label-width="120px"
        class="role-form"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input
            v-model="roleForm.name"
            placeholder="请输入角色名称"
          />
        </el-form-item>

        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRole" :loading="loading">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 分配用户对话框 -->
    <el-dialog
      v-model="assignDialogVisible"
      title="分配用户"
      width="800px"
      @close="handleAssignDialogClose"
    >
      <div class="assign-users-container">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="available-users">
              <h4>可用用户</h4>
              <el-input
                v-model="availableUsersFilter"
                placeholder="搜索用户"
                style="margin-bottom: 10px"
              >
                <template #append>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-select
                v-model="selectedAvailableUsers"
                multiple
                filterable
                placeholder="请选择用户"
                style="width: 100%; height: 300px"
                :popper-append-to-body="false"
              >
                <el-option
                  v-for="user in filteredAvailableUsers"
                  :key="user.id"
                  :label="user.name + ' (' + user.username + ')'
                  :value="user.id"
                />
              </el-select>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="assigned-users">
              <h4>已分配用户</h4>
              <el-input
                v-model="assignedUsersFilter"
                placeholder="搜索用户"
                style="margin-bottom: 10px"
              >
                <template #append>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-select
                v-model="selectedAssignedUsers"
                multiple
                filterable
                placeholder="请选择用户"
                style="width: 100%; height: 300px"
                :popper-append-to-body="false"
              >
                <el-option
                  v-for="user in filteredAssignedUsers"
                  :key="user.id"
                  :label="user.name + ' (' + user.username + ')'
                  :value="user.id"
                />
              </el-select>
            </div>
          </el-col>
        </el-row>
        <div class="assign-buttons">
          <el-button @click="handleAssignSelected">
            <el-icon><ArrowRight /></el-icon>
            分配
          </el-button>
          <el-button @click="handleUnassignSelected">
            <el-icon><ArrowLeft /></el-icon>
            移除
          </el-button>
        </div>
      </div>

      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveAssignments" :loading="assignLoading">
          <el-icon><Check /></el-icon>
          保存分配
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Check, Search, ArrowRight, ArrowLeft } from '@element-plus/icons-vue'

const formRef = ref(null)
const dialogVisible = ref(false)
const assignDialogVisible = ref(false)
const loading = ref(false)
const assignLoading = ref(false)
const editingRole = ref({})
const currentRole = ref({})
const roles = ref([])
const allUsers = ref([])
const availableUsers = ref([])
const assignedUsers = ref([])
const selectedAvailableUsers = ref([])
const selectedAssignedUsers = ref([])
const availableUsersFilter = ref('')
const assignedUsersFilter = ref('')

// 表单数据
const roleForm = reactive({
  name: '',
  description: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '角色描述长度不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 过滤后的可用用户
const filteredAvailableUsers = computed(() => {
  if (!availableUsersFilter.value) {
    return availableUsers.value
  }
  return availableUsers.value.filter(user => 
    user.name.toLowerCase().includes(availableUsersFilter.value.toLowerCase()) ||
    user.username.toLowerCase().includes(availableUsersFilter.value.toLowerCase()) ||
    user.email.toLowerCase().includes(availableUsersFilter.value.toLowerCase())
  )
})

// 过滤后的已分配用户
const filteredAssignedUsers = computed(() => {
  if (!assignedUsersFilter.value) {
    return assignedUsers.value
  }
  return assignedUsers.value.filter(user => 
    user.name.toLowerCase().includes(assignedUsersFilter.value.toLowerCase()) ||
    user.username.toLowerCase().includes(assignedUsersFilter.value.toLowerCase()) ||
    user.email.toLowerCase().includes(assignedUsersFilter.value.toLowerCase())
  )
})

// 添加角色
const handleAddRole = () => {
  editingRole.value = {}
  resetForm()
  dialogVisible.value = true
}

// 编辑角色
const handleEditRole = (role) => {
  editingRole.value = { ...role }
  Object.assign(roleForm, {
    name: role.name,
    description: role.description || ''
  })
  dialogVisible.value = true
}

// 保存角色
const handleSaveRole = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const roleData = { ...roleForm }
    
    if (editingRole.value.id) {
      // 编辑模式
      await $axios.put(`/roles/${editingRole.value.id}`, roleData)
      ElMessage.success('角色更新成功')
    } else {
      // 创建模式
      await $axios.post('/roles/', roleData)
      ElMessage.success('角色创建成功')
    }
    
    dialogVisible.value = false
    loadRoles()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(editingRole.value.id ? '更新失败' : '创建失败')
  } finally {
    loading.value = false
  }
}

// 删除角色
const handleDeleteRole = async (roleId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个角色吗？', '确认删除', {
      type: 'warning'
    })
    
    await $axios.delete(`/roles/${roleId}`)
    ElMessage.success('角色删除成功')
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 分配用户
const handleAssignUsers = (role) => {
  currentRole.value = { ...role }
  assignDialogVisible.value = true
  loadUsersForRole(role.id)
}

// 加载角色的用户列表
const loadUsersForRole = async (roleId) => {
  try {
    const response = await $axios.get(`/roles/${roleId}/users`)
    const { available, assigned } = response.data
    availableUsers.value = available || []
    assignedUsers.value = assigned || []
    selectedAvailableUsers.value = []
    selectedAssignedUsers.value = []
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  }
}

// 分配选中的用户
const handleAssignSelected = () => {
  selectedAvailableUsers.value.forEach(userId => {
    const user = availableUsers.value.find(u => u.id === userId)
    if (user) {
      assignedUsers.value.push(user)
      availableUsers.value = availableUsers.value.filter(u => u.id !== userId)
    }
  })
  selectedAvailableUsers.value = []
}

// 移除选中的用户
const handleUnassignSelected = () => {
  selectedAssignedUsers.value.forEach(userId => {
    const user = assignedUsers.value.find(u => u.id === userId)
    if (user) {
      availableUsers.value.push(user)
      assignedUsers.value = assignedUsers.value.filter(u => u.id !== userId)
    }
  })
  selectedAssignedUsers.value = []
}

// 保存用户分配
const handleSaveAssignments = async () => {
  try {
    assignLoading.value = true
    
    const userIds = assignedUsers.value.map(user => user.id)
    await $axios.put(`/roles/${currentRole.value.id}/users`, { user_ids: userIds })
    
    ElMessage.success('用户分配成功')
    assignDialogVisible.value = false
    loadRoles() // 重新加载角色列表以更新用户计数
  } catch (error) {
    console.error('分配失败:', error)
    ElMessage.error('分配失败')
  } finally {
    assignLoading.value = false
  }
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
  editingRole.value = {}
}

// 关闭分配用户对话框
const handleAssignDialogClose = () => {
  currentRole.value = {}
  availableUsers.value = []
  assignedUsers.value = []
  selectedAvailableUsers.value = []
  selectedAssignedUsers.value = []
  availableUsersFilter.value = ''
  assignedUsersFilter.value = ''
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 加载角色列表
const loadRoles = async () => {
  try {
    const response = await $axios.get('/roles/')
    roles.value = response.data.roles || []
  } catch (error) {
    console.error('加载角色列表失败:', error)
    ElMessage.error('加载角色列表失败')
  }
}

// 加载所有用户（用于分配用户时的选择）
const loadAllUsers = async () => {
  try {
    const response = await $axios.get('/users/')
    allUsers.value = response.data.users || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  }
}

onMounted(() => {
  loadRoles()
  loadAllUsers()
})
</script>

<style scoped>
.role-list-container {
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

.role-list-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.role-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.role-form {
  padding: 20px 0;
}

.assign-users-container {
  padding: 20px 0;
}

.available-users,
.assigned-users {
  height: 100%;
}

.available-users h4,
.assigned-users h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
}

.assign-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}
</style>