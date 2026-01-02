<script setup>
import { ref, onMounted, watch } from 'vue'
import Navbar from './components/Navbar.vue'
import RegisterForm from './components/RegisterForm.vue'
import Login from './components/Login.vue' 
import User from './components/User.vue'
import SpotForm from './components/SpotForm.vue'
import Home from './components/Home.vue' 
import AIPlanner from './components/AIPlanner.vue'

const currentPage = ref('home')
const isDarkMode = ref(false)
const user = ref(null)
const currentCategory = ref('全部');

// 切換頁面
const switchPage = (pageName) => {
  currentPage.value = pageName
  window.scrollTo({top: 0, behavior: 'smooth'})
}

// 處理篩選 (如果您的 Home.vue 有實作接收這個 prop，可以傳進去，這裡先保留 console)
const handleFilter = (location) => {
  console.log('篩選地點:', location)
}

// 處理登入成功
const handleLoginSuccess = (userData) => {
  // 如果 Login 元件回傳了 user 資料，直接使用
  if (userData) {
    user.value = userData;
    localStorage.setItem('user', JSON.stringify(userData));
  } else {
    // 否則從 localStorage 讀取
    const storeUser = localStorage.getItem('user');
    if (storeUser) {
      user.value = JSON.parse(storeUser);
    }
  }
  switchPage('home'); // 登入後通常跳轉首頁或個人頁
}

const handleCategorySelect = (category) => {
  currentCategory.value = category; // 更新分類
  switchPage('home'); // 確保切換回首頁
};

// 處理登出 (Navbar 觸發)
const handleLogout = () => {
    user.value = null;
    localStorage.removeItem('user');
    localStorage.removeItem('token'); // 如果有存 token 也要清
    switchPage('login');
}

// 切換主題模式
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

// 網頁載入時讀取設定
onMounted(() => {
  // 1. 讀取主題
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDarkMode.value = true
  }
  
  // 2. 讀取使用者
  const storeUser = localStorage.getItem('user');
  if (storeUser) {
    try {
        user.value = JSON.parse(storeUser);
    } catch (e) {
        console.error("User data parse error", e);
        localStorage.removeItem('user');
    }
  }

  // 3. 如果已登入，您原本的邏輯是跳轉到 User 頁，這裡保留您的設定
  // (通常一般網站會預設留首頁，但這裡照您的需求)
  if(localStorage.getItem('token') && user.value) {
    // currentPage.value = 'user'; 
  }
})

// 監聽主題變化
watch(isDarkMode, (newVal) => {
  document.body.style.backgroundColor = newVal ? '#121212' : '#fafafa'
})

// 監聽 user 狀態 (如果 user 變成 null，自動跳轉登入頁)
watch(user, (newVal) => {
  if(!newVal) {
    // currentPage.value = 'login'; 
  }
})
</script>

<template>
  <div class="app-wrapper" :class="{'dark-mode': isDarkMode }">
    
    <Navbar 
      :activePage="currentPage" 
      :isDarkMode="isDarkMode"
      :userName="user ? user.name : ''"
      @changePage="switchPage"
      @filterLocation="handleFilter"  
      @toggleTheme="toggleTheme"
      @logout="handleLogout"
      @selectCategory="handleCategorySelect"
    />

    <main class="content-area">
      
      <div v-if="currentPage === 'home'">
        <Home 
            :user="user"
            :initialCategory="currentCategory"
         />
      </div>

      <div v-if="currentPage === 'add'">
        <SpotForm @submitSuccess="switchPage('home')" />
      </div>

      <div v-if="currentPage === 'register'">
        <RegisterForm 
          @registerSuccess="switchPage('login')" 
          @changePage="switchPage" 
        />
      </div>

      <div v-if="currentPage === 'login'">
        <Login @loginSuccess="handleLoginSuccess" />
      </div>

      <div v-if="currentPage === 'user'">
        <User 
            :user="user" 
            @changePage="switchPage" 
        />
      </div>

      <div v-if="currentPage === 'ai_planner'">
          <AIPlanner />
      </div>
    </main>
  </div>
</template>

<style>
/* 您的 CSS 樣式完全保持不變 */
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

/* 如果您的 Home.vue 已經包含了 hero-header，這裡的樣式可以留著給 Home.vue 用，
   或者如果 Home.vue 有 scoped style，這裡也可以保留作為全域預設值 */
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