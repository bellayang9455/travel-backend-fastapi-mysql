<script setup>
import { ref } from 'vue'
import SpotForm from './components/SpotForm.vue'
import SpotList from './components/SpotList.vue'
import Navbar from './components/Navbar.vue'

// 1. 定義一個變數來記錄現在要在哪一頁
// 預設是 'home' (主畫面/列表頁)
const currentPage = ref('home')

// 切換頁面的功能
const switchPage = (pageName) => {
  currentPage.value = pageName
  window.scrollTo({top:0, behavior: 'smooth'}) // 切換頁面時捲動到最上方
}
const handleFilter = (location) => {
  console.log('使用者選了地點:', location)
  // 目前先印出來就好，之後再做篩選功能
}   
</script>

<template>
  <div class="min-h-screen bg-gray-50 font-sans text-gray-900">
    
    <Navbar 
      :activePage="currentPage" 
      @changePage="switchPage"
      @filterLocation="handleFilter"
    />

    <main class="max-w-7xl mx-auto py-8 px-4">
      
      <div v-if="currentPage === 'home'">
        <div class="mb-8 text-center">
          <h2 class="text-3xl font-bold text-gray-800 mb-2">探索世界之美</h2>
          <!--<p class="text-gray-500">紀錄每一個感動的瞬間</p>-->
        </div>
        <SpotList />
      </div>

      <div v-if="currentPage === 'add'">
        <SpotForm />
      </div>

    </main>
  </div>
</template>
