// src/router/index.js
// 關於 Vue Router 的設定檔案
// 用來頁面之間的導航
import { createRouter, createWebHistory } from 'vue-router'

// 引入你的元件 (請確認路徑與檔名是否正確)
import RegisterForm from '../components/RegisterForm.vue'
import Login from '../components/Login.vue' 
import User from '../components/User.vue'
import SpotForm from '../components/SpotForm.vue'
import Home from '../components/Home.vue' 
import AIPlanner from '../components/AIPlanner.vue'
// 如果你有註冊頁面
// import Register from '../components/Register.vue' 

const routes = [
  { path: '/', name: 'home', component: Home }, // 首頁路由
  { path: '/login', name: 'login', component: Login }, // 登入頁路由
  { path: '/register', name: 'register', component: RegisterForm }, // 註冊頁路由
  { path: '/ai-planner', name: 'ai-planner', component: AIPlanner },
  { path: '/user', name: 'user', component: User }, // 使用者資料頁路由
  { path: '/add', name: 'add', component: SpotForm } // 新增景點頁路由
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router