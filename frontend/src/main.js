import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 引入Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入Element Plus图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 引入Axios
import axios from 'axios'

// 引入Vue Router
import router from './router'

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 配置Axios
axios.defaults.baseURL = '/api'
app.config.globalProperties.$axios = axios

// 使用Element Plus
app.use(ElementPlus)

// 使用Vue Router
app.use(router)

app.mount('#app')
