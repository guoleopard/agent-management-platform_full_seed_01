import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import ModelList from '../views/ModelList.vue'
import AgentList from '../views/AgentList.vue'
import UserList from '../views/UserList.vue'
import RoleList from '../views/RoleList.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/models',
    children: [
      {
        path: 'models',
        name: 'ModelList',
        component: ModelList,
        meta: { title: '模型管理' }
      },
      {
        path: 'agents',
        name: 'AgentList',
        component: AgentList,
        meta: { title: 'Agent管理' }
      },
      {
        path: 'users',
        name: 'UserList',
        component: UserList,
        meta: { title: '用户管理' }
      },
      {
        path: 'roles',
        name: 'RoleList',
        component: RoleList,
        meta: { title: '角色管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置页面标题
router.beforeEach((to, from) => {
  if (to.meta.title) {
    document.title = to.meta.title + ' - Agent Platform'
  }
})

export default router