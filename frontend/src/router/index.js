import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import ModelList from '../views/ModelList.vue'
import AgentList from '../views/AgentList.vue'

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
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title + ' - Agent Platform'
  }
  next()
})

export default router