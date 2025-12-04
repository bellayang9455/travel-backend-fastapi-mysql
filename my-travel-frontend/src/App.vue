<script setup>
import SpotForm from './components/SpotForm.vue'
import SpotList from './components/SpotList.vue'
</script>

<template>
  <div class="main-container">
    <h1>✈️ 我的旅遊日記</h1>
    
    <SpotForm />
    
    <SpotList />
  </div>
</template>

<style>
/* 全域設定 */
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: #f8f9fa;
}
.main-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}
h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}
</style>