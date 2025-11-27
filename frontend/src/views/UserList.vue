<template>
  <div class="user-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="handleAddUser">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>

    <!-- 用户列表 -->
    <el-card class="user-list-card">
      <div class="user-list">
        <el-table :data="users" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="role_name" label="角色" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-switch
                v-model="scope.row.status"
                :active-value="1"
                :inactive-value="0"
                @change="handleStatusChange(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column prop="updated_at" label="更新时间" width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="handleEditUser(scope.row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDeleteUser(scope.row.id)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 用户表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingUser.id ? '编辑用户' : '添加用户'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="userForm"
        :rules="rules"
        label-width="120px"
        class="user-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="userForm.email"
            placeholder="请输入邮箱"
          />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="userForm.name"
            placeholder="请输入姓名"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password" v-if="!editingUser.id">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password" v-if="!editingUser.id">
          <el-input
            v-model="userForm.confirm_password"
            type="password"
            placeholder="请确认密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="角色" prop="role_id">
          <el-select
            v-model="userForm.role_id"
            placeholder="请选择角色"
          >
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="userForm.status"
            :active-value="1"
            :inactive-value="0"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser" :loading="loading">
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
const editingUser = ref({})
const users = ref([])
const roles = ref([])

// 表单数据
const userForm = reactive({
  username: '',
  email: '',
  name: '',
  password: '',
  confirm_password: '',
  role_id: '',
  status: 1
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role_id: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 验证确认密码
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== userForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 添加用户
const handleAddUser = () => {
  editingUser.value = {}
  resetForm()
  dialogVisible.value = true
}

// 编辑用户
const handleEditUser = (user) => {
  editingUser.value = { ...user }
  Object.assign(userForm, {
    username: user.username,
    email: user.email,
    name: user.name,
    role_id: user.role_id,
    status: user.status
  })
  dialogVisible.value = true
}

// 保存用户
const handleSaveUser = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const userData = { ...userForm }
    if (editingUser.value.id) {
      // 编辑模式，删除不需要的字段
      delete userData.password
      delete userData.confirm_password
      await $axios.put(`/users/${editingUser.value.id}`, userData)
      ElMessage.success('用户更新成功')
    } else {
      // 创建模式
      await $axios.post('/users/', userData)
      ElMessage.success('用户创建成功')
    }
    
    dialogVisible.value = false
    loadUsers()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(editingUser.value.id ? '更新失败' : '创建失败')
  } finally {
    loading.value = false
  }
}

// 删除用户
const handleDeleteUser = async (userId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用户吗？', '确认删除', {
      type: 'warning'
    })
    
    await $axios.delete(`/users/${userId}`)
    ElMessage.success('用户删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 更改用户状态
const handleStatusChange = async (user) => {
  try {
    await $axios.put(`/users/${user.id}`, {
      status: user.status
    })
    ElMessage.success('用户状态更新成功')
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
    // 恢复原来的状态
    user.status = user.status === 1 ? 0 : 1
  }
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
  editingUser.value = {}
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  userForm.password = ''
  userForm.confirm_password = ''
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await $axios.get('/users/')
    users.value = response.data.users || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
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

onMounted(() => {
  loadUsers()
  loadRoles()
})
</script>

<style scoped>
.user-list-container {
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

.user-list-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.user-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.user-form {
  padding: 20px 0;
}
</style>