<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="layout-aside">
      <div class="logo">
        <el-icon size="32"><ChatDotRound /></el-icon>
        <span>Agent Platform</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="layout-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="models">
          <el-icon><Setting /></el-icon>
          <span>模型管理</span>
        </el-menu-item>
        <el-menu-item index="agents">
          <el-icon><Plus /></el-icon>
          <span>Agent管理</span>
        </el-menu-item>
        <el-menu-item index="users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="roles">
          <el-icon><UserFilled /></el-icon>
          <span>角色管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区域 -->
    <el-container class="main-container">
      <el-header class="layout-header">
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-icon size="20"><User /></el-icon>
              管理员
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ChatDotRound, Setting, Plus, User, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const activeMenu = ref('model-settings')

const handleMenuSelect = (key) => {
  activeMenu.value = key
  router.push(`/${key}`)
}

onMounted(() => {
  // 根据当前路由设置激活的菜单
  const path = route.path.slice(1) // 去除开头的'/'
  if (path) {
    activeMenu.value = path
  }
})
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.layout-aside {
  background-color: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64px;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #1f2f3f;
}

.logo span {
  margin-left: 8px;
}

.layout-menu {
  flex: 1;
  border: none;
  background-color: transparent;
}

.el-menu-item {
  color: rgba(255, 255, 255, 0.65);
  border-bottom: 1px solid #1f2f3f;
}

.el-menu-item:hover,
.el-menu-item.is-active {
  color: #fff;
  background-color: #1890ff;
}

.el-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.layout-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.user-info:hover {
  color: #1890ff;
}

.user-info el-icon {
  margin-right: 4px;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-main {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f5f5;
}
</style>