<script setup>
import { ref, onMounted, watch } from 'vue'
import SpotForm from './components/SpotForm.vue'
import SpotList from './components/SpotList.vue'
import Navbar from './components/Navbar.vue'
import RegisterForm from './components/RegisterForm.vue' // ⭐ 1. 引入註冊組件

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
  // 儲存設定到瀏覽器
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

// 網頁載入時讀取設定
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDarkMode.value = true
  }
})

// 監聽模式改變，同步修改 body 背景色
watch(isDarkMode, (newVal) => {
  document.body.style.backgroundColor = newVal ? '#121212' : '#fafafa'
})
</script>

<template>
  <div class="app-wrapper" :class="{'dark-mode': isDarkMode }">
    
    <!-- 導覽列 -->
    <Navbar 
      :activePage="currentPage" 
      :isDarkMode="isDarkMode"
      @changePage="switchPage"
      @filterLocation="handleFilter"  
      @toggleTheme="toggleTheme"
    />

    <!-- 內容區域 -->
    <main class="content-area">
      
      <!-- 首頁內容 -->
      <div v-if="currentPage === 'home'">
        <div class="hero-header">
          <h2>探索世界之美</h2>
          <p>紀錄每一個感動的瞬間</p>
        </div>
        
        <SpotList />
      </div>

      <!-- 新增頁面內容 -->
      <div v-if="currentPage === 'add'">
        <SpotForm />
      </div>

      <!-- ⭐ 2. 註冊頁面內容 -->
      <div v-if="currentPage === 'register'">
        <RegisterForm />
      </div>

    </main>
  </div>
</template>

<style>
/* CSS 保持原樣，不需要變動 */
:root {
  /* 白天模式 (預設) */
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

/* 深色模式 */
.dark-mode {
  --bg-color: #121212;         /* 極深灰背景 */
  --text-color: #e0e0e0;       /* 淺灰文字 */
  --text-secondary: #aaa;      /* 次要文字 */
  --card-bg: #1e1e1e;          /* 卡片深灰 */
  --border-color: #333;        /* 深色邊框 */
  --nav-bg: #1e1e1e;           /* 導覽列深灰 */
  --input-bg: #2d2d2d;         /* 輸入框背景 */
  --input-border: #444;        /* 輸入框邊框 */
  --shadow-color: rgba(0,0,0,0.5); /* 深色陰影 */
  --primary-color: #66bb6a;    /* 綠色亮一點 */
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