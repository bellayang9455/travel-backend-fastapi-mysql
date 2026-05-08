<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import Login from './components/Login.vue'               // 新增引入
import RegisterForm from './components/RegisterForm.vue' // 新增引入

const router = useRouter()
const route = useRoute()
const isDarkMode = ref(false)
const user = ref(null)

// --- 👇 彈窗控制邏輯 👇 ---
const showLoginModal = ref(false)
const showRegisterModal = ref(false)

const openLogin = () => {
  showLoginModal.value = true
  showRegisterModal.value = false
}

const openRegister = () => {
  showRegisterModal.value = true
  showLoginModal.value = false
}

const closeModals = () => {
  showLoginModal.value = false
  showRegisterModal.value = false
}
// --- 👆 彈窗控制邏輯 👆 ---

const currentCategory = ref('全部')

const switchPage = (pageName) => {
  if (pageName === 'home') {
    currentCategory.value = '全部'
    router.push({ path: '/' })
    return
  }
  
  const routeMap = {
    'home': 'home',
    'add': 'add',
    'user': 'user',
    'ai_planner': 'ai-planner'
  }
  
  const targetRoute = routeMap[pageName] || 'home'
  router.push({ name: targetRoute })
}

const handleSelectCategory = (categoryName) => {
  currentCategory.value = categoryName
  switchPage('home')
}

const handleFilterLocation = (locationValue) => {
  const currentQuery = { ...route.query }
  if (locationValue === '') {
    delete currentQuery.location
  } else {
    currentQuery.location = locationValue
  }
  router.push({ path: '/', query: currentQuery })
}

// --- 👇 修改登入與註冊成功處理 👇 ---
const handleLoginSuccess = (userData) => {
  if (userData) {
    user.value = userData
    sessionStorage.setItem('user', JSON.stringify(userData))
  }
  closeModals() // 登入成功後關閉彈窗
}

const handleRegisterSuccess = (userData) => {
  if (userData) {
    user.value = userData
    sessionStorage.setItem('user', JSON.stringify(userData))
  }
  closeModals() // 註冊成功後關閉彈窗
  alert('註冊成功！已自動為您登入。')
}
// --- 👆 修改登入與註冊成功處理 👆 ---

const handleLogout = () => {
  user.value = null
  sessionStorage.removeItem('user')
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('user_name')
  sessionStorage.removeItem('user_id')
  alert('已登出')
  router.push({ name: 'home' }) // 登出後回首頁
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') isDarkMode.value = true
  
  const token = sessionStorage.getItem('token')
  const storeUser = sessionStorage.getItem('user')

  if (token && storeUser) {
      try {
      user.value = JSON.parse(storeUser)
    } catch (e) {
      user.value = null
    }
  }
})

watch(isDarkMode, (newVal) => {
  document.body.style.backgroundColor = newVal ? '#121212' : '#fafafa'
})
</script>

<template>
  <div class="app-wrapper" :class="{'dark-mode': isDarkMode }">
    
    <Navbar 
      :activePage="route.name" 
      :isDarkMode="isDarkMode"
      :user-name="user ? user.name : ''"
      :user-id="user ? user.id : ''"
      :isLoggedIn="!!user"
      @changePage="switchPage"
      @toggleTheme="toggleTheme"
      @logout="handleLogout"
      @selectCategory="handleSelectCategory" 
      @filterLocation="handleFilterLocation"
      @openLogin="openLogin"         
    />

    <main class="content-area">
      <router-view v-slot="{ Component }">
        <keep-alive include="AIPlanner">
          <component 
            :is="Component" 
            :user="user"
            :initialCategory="currentCategory" 
            :isLoggedIn="!!user"
            @loginSuccess="handleLoginSuccess"
            @submitSuccess="() => router.push({ name: 'home' })"
            @changePage="switchPage"
          />
        </keep-alive>
      </router-view>
    </main>

    <div v-if="showLoginModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-card">
        <button class="modal-close" @click="closeModals">✕</button>
        <Login @loginSuccess="handleLoginSuccess" @changePage="openRegister" />
      </div>
    </div>

    <div v-if="showRegisterModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-card">
        <button class="modal-close" @click="closeModals">✕</button>
        <RegisterForm @registerSuccess="handleRegisterSuccess" @changePage="openLogin" />
      </div>
    </div>

  </div>
</template>

<style>
/* ...保留你原本所有的 CSS... */
:root {
  --bg-color: #fafafa;
  --text-color: #2c3e50;
  --text-secondary: #666;
  --card-bg: #ffffff;
  --border-color: #eee;
  --nav-bg: #ffffff;
  --input-bg: #fafafa;
  --input-border: #ddd;
  --shadow-color: rgba(0,0,0,0.05);
  --primary-color: #4CAF50;
  --link-color: #333;
}

.dark-mode {
  --bg-color: #121212;
  --text-color: #e0e0e0;
  --text-secondary: #aaa;
  --card-bg: #1e1e1e;
  --border-color: #333;
  --nav-bg: #1e1e1e;
  --input-bg: #2d2d2d;
  --input-border: #444;
  --shadow-color: rgba(0,0,0,0.5);
  --primary-color: #66bb6a;
  --link-color: #e0e0e0;
}

body {
  margin: 0 !important;
  padding: 0 !important;
  background-color: var(--bg-color);
  font-family: '微軟正黑體', Arial, sans-serif;
  overflow-x: hidden;
  transition: background-color 0.3s;
}

.app-wrapper {
  min-height: 100vh;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.content-area {
  padding-top: 80px; 
  max-width: 1200px; 
  margin: 0 auto; 
  padding-left: 20px;
  padding-right: 20px;
  padding-bottom: 60px;
  min-height: 100vh;
}

.hero-header {
  text-align: center;
  margin-bottom: 40px;
  margin-top: 20px;
}

.hero-header h2 {
  font-size: 2rem;
  font-weight: bold;
  color: var(--text-color); 
  margin-bottom: 10px;
  letter-spacing: 2px;
}

.hero-header p {
  color: var(--text-secondary);
  font-size: 1rem;
}

/* 👇 新增：彈窗 Modal 的 CSS 👇 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(3px);
}

.modal-card {
  background: var(--card-bg);
  padding: 10px;
  border-radius: 16px;
  position: relative;
  width: 90%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  animation: fadeInDown 0.3s ease-out;
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 20px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  z-index: 10;
}

.modal-close:hover {
  color: var(--text-color);
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>