<script setup>
import { ref } from 'vue'
import SpotForm from './components/SpotForm.vue'
import SpotList from './components/SpotList.vue'

// 1. 定義一個變數來記錄現在要在哪一頁
// 預設是 'home' (主畫面/列表頁)
const currentPage = ref('home')

// 切換頁面的功能
const switchPage = (pageName) => {
  currentPage.value = pageName
}
</script>

<template>
  <div class="main-container">
    <h1>✈️ 我的旅遊日記</h1>

    <div class="nav-area">
      <button 
        v-if="currentPage === 'home'" 
        @click="switchPage('add')" 
        class="btn-add"
      >
        ➕ 我要新增景點
      </button>

      <button 
        v-if="currentPage === 'add'" 
        @click="switchPage('home')" 
        class="btn-back"
      >
        ⬅️ 返回列表
      </button>
    </div>
    
    <div v-if="currentPage === 'home'">
      <SpotList />
    </div>

    <div v-if="currentPage === 'add'">
      <SpotForm />
    </div>

  </div>
</template>

<style>
/* 全域設定 */
body {
  margin: 0;
  padding: 0;
  background-color: #4994e0;
  font-family: '微軟正黑體', Arial, sans-serif;
}

.main-container {
  max-width: 800px; 
  margin: 0 auto; 
  padding: 60px;
  min-height: 100vh;
  background-color: white;
  box-shadow: 0 0 15px rgba(0,0,0,0.05);
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  letter-spacing: 2px;
}

/* 按鈕區域設定 */
.nav-area {
  text-align: right; /* 按鈕靠右邊比較順手 */
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #eee; /* 加條線區隔 */
}

/* 新增按鈕樣式 */
.btn-add {
  background-color: #42b983; /* Vue 的綠色 */
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 25px; /* 圓角 */
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.btn-add:hover {
  background-color: #3aa876;
  transform: translateY(-2px); /* 浮起來的效果 */
}

/* 返回按鈕樣式 */
.btn-back {
  background-color: #607d8b; /* 灰藍色 */
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
}

.btn-back:hover {
  background-color: #546e7a;
}
</style>