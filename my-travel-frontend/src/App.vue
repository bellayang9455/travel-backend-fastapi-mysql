<script setup>
// App.vue 是整個應用的根組件，負責管理全局狀態如使用者登入狀態和主題切換
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'

const router = useRouter()
const route = useRoute() // 用來監聽網址變化
const isDarkMode = ref(false)
const user = ref(null)

// ✨ 新增：用來記住使用者目前在側邊欄選了什麼分類
const currentCategory = ref('全部')

// --- 導航邏輯 ---
const switchPage = (pageName) => {
  const routeMap = {
    'home': 'home',
    'add': 'add',
    'register': 'register',
    'login': 'login',
    'user': 'user',
    'ai_planner': 'ai-planner'
  }
  
  const targetRoute = routeMap[pageName] || 'home'
  router.push({ name: targetRoute })
}

// ✨ 新增：接收 Navbar 傳來的分類點擊事件
const handleSelectCategory = (categoryName) => {
  currentCategory.value = categoryName
  switchPage('home') // 切換分類時，確保跳回首頁看結果
}

// --- 登入成功處理 ---
const handleLoginSuccess = (userData) => {
  if (userData) {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }
  router.push({ name: 'home' })
}

// --- 登出處理 ---
const handleLogout = () => {
  user.value = null
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  localStorage.removeItem('user_name')
  localStorage.removeItem('user_id')
  alert('已登出')
  router.push({ name: 'login' })
}

// --- 主題切換 ---
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

// --- 初始化 ---
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') isDarkMode.value = true
  
  const token = localStorage.getItem('token')
  const storeUser = localStorage.getItem('user')
  
  if (token && storeUser) {
    try {
      user.value = JSON.parse(storeUser)
    } catch (e) {
      console.error("User parse error", e)
    }
  }
})

// --- 監聽主題 ---
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
            @registerSuccess="handleLoginSuccess"
            @submitSuccess="() => router.push({ name: 'home' })"
            @changePage="switchPage"
          />
        </keep-alive>
      </router-view>
    </main>
  </div>
</template>

<style>
/* CSS 完全保持不變，不用動 */
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
</style>