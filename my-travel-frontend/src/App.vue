<script setup>
import { ref, onMounted, watch } from 'vue'
import SpotForm from './components/SpotForm.vue'
import SpotList from './components/SpotList.vue'
import Navbar from './components/Navbar.vue'
import RegisterForm from './components/RegisterForm.vue'
import Login from './components/Login.vue' // Login 元件
import User from './components/User.vue'   // User 元件

const currentPage = ref('home')
const isDarkMode = ref(false)

const switchPage = (pageName) => {
  currentPage.value = pageName
  window.scrollTo({top: 0, behavior: 'smooth'})
}

const handleFilter = (location) => {
  console.log('篩選地點:', location)
}

// 切換主題模式
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

// 網頁載入時讀取設定
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDarkMode.value = true
  }
  
  // 如果使用者在 localStorage 裡有 token，代表登入過，可以直接顯示 user 頁 (選用)
  /*
  if (localStorage.getItem('token')) {
    currentPage.value = 'user'
  }
  */
})

watch(isDarkMode, (newVal) => {
  document.body.style.backgroundColor = newVal ? '#121212' : '#fafafa'
})
</script>

<template>
  <div class="app-wrapper" :class="{'dark-mode': isDarkMode }">
    
    <Navbar 
      :activePage="currentPage" 
      :isDarkMode="isDarkMode"
      @changePage="switchPage"
      @filterLocation="handleFilter"  
      @toggleTheme="toggleTheme"
    />

    <main class="content-area">
      
      <div v-if="currentPage === 'home'">
        <div class="hero-header">
          <h2>探索世界之美</h2>
          <p>紀錄每一個感動的瞬間</p>
        </div>
        <SpotList />
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
        <Login @loginSuccess="switchPage('user')" />
      </div>

      <div v-if="currentPage === 'user'">
        <User />
      </div>

    </main>
  </div>
</template>

<style>
/* 您的 CSS 樣式保持不變 */
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