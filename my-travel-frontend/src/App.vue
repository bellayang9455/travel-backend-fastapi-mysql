<script setup>
import { ref } from 'vue'
import SpotForm from './components/SpotForm.vue'
import SpotList from './components/SpotList.vue'
import Navbar from './components/Navbar.vue'

const currentPage = ref('home')

const switchPage = (pageName) => {
  currentPage.value = pageName
  window.scrollTo({top: 0, behavior: 'smooth'})
}

const handleFilter = (location) => {
  console.log('篩選地點:', location)
}
</script>

<template>
  <div class="app-wrapper">
    
    <!-- 導覽列放在最外面，確保滿版 -->
    <Navbar 
      :activePage="currentPage" 
      @changePage="switchPage"
      @filterLocation="handleFilter" 
    />

    <!-- 內容區域 -->
    <main class="content-area">
      
      <!-- 首頁內容 -->
      <div v-if="currentPage === 'home'">
        <!-- 標題區塊 (改用 CSS 設定樣式) -->
        <div class="hero-header">
          <h2>探索世界之美</h2>
          <p>紀錄每一個感動的瞬間</p>
        </div>
        
        <!-- 景點列表 -->
        <SpotList />
      </div>

      <!-- 新增頁面內容 -->
      <div v-if="currentPage === 'add'">
        <SpotForm />
      </div>

    </main>
  </div>
</template>

<style>
/* 1. 全域設定：清除邊距 */
body {
  margin: 0 !important;
  padding: 0 !important;
  background-color: #fafafa;
  font-family: '微軟正黑體', Arial, sans-serif;
  overflow-x: hidden;
}

/* 2. 內容區域設定 */
.content-area {
  /* 往下推 80px，避免被導覽列擋住 (因為 Navbar 高度約 64px) */
  padding-top: 80px; 
  
  /* 限制內容最大寬度，並置中 */
  max-width: 1200px; 
  margin: 0 auto; 
  
  /* 左右留一點縫隙 */
  padding-left: 20px;
  padding-right: 20px;
  padding-bottom: 60px;
  
  min-height: 100vh;
}

/* 3. 標題區塊樣式 (取代 Tailwind) */
.hero-header {
  text-align: center;
  margin-bottom: 40px;
  margin-top: 20px;
}

.hero-header h2 {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
  letter-spacing: 2px;
}

.hero-header p {
  color: #888;
  font-size: 1rem;
}
.isDarkMode {
  background-color: #121212;
  color: #e0e0e0;
}
</style>