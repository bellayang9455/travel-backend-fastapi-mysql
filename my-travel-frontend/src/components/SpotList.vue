<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 定義一個變數來裝從後端抓來的景點資料
const spots = ref([])

// 抓資料的函式
const fetchSpots = async () => {
  try {
    // ⚠️ 注意：這裡的網址要改成您後端真正提供景點列表的 API 路徑
    // 您可以去 http://127.0.0.1:8000/docs 查查看，通常是 /spots
    const response = await axios.get('http://127.0.0.1:8000/spots')
    spots.value = response.data
  } catch (error) {
    console.error("抓不到資料:", error)
  }
}

// 畫面一載入就執行
onMounted(() => {
  fetchSpots()
})
</script>

<template>
  <div class="spot-container">
    <h2>🏖️ 熱門景點列表</h2>
    
    <div class="grid">
      <div v-for="spot in spots" :key="spot.id" class="card">
        <img :src="spot.image_url || 'https://placehold.co/600x400'" alt="景點圖片">
        <div class="card-body">
          <h3>{{ spot.name }}</h3>
          <p>{{ spot.description }}</p>
          <span class="tag">{{ spot.address }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 簡單的卡片 CSS 設計 */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); /* 自動排版 */
  gap: 20px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: transform 0.2s;
  background: white;
}

.card:hover {
  transform: translateY(-5px); /* 滑鼠移過去會浮起來 */
}

.card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.card-body {
  padding: 15px;
}

.tag {
  font-size: 12px;
  color: #666;
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
}
</style>