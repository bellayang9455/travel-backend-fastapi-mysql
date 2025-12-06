<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const spots = ref([])
const loading = ref(true)

// 隨機產生圖片
const getImageUrl = (id) => {
  return `https://picsum.photos/seed/${id}/400/300`
}

const fetchSpots = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/spots')
    spots.value = response.data
  } catch (error) {
    console.error("抓不到資料:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSpots()
})
</script>

<template>
  <div class="spot-container">
    
    <div class="header">
      <h2>🏝️ 熱門景點列表</h2>
      <span class="count">共 {{ spots.length }} 個景點</span>
    </div>

    <div v-if="loading" class="loading">
      ⏳ 載入景點中...
    </div>

    <div v-else class="grid-layout">
      
      <div v-for="spot in spots" :key="spot.id" class="card">
        
        <div class="image-box">
          <img :src="getImageUrl(spot.id)" alt="景點圖片">
          <span class="category-tag">{{ spot.category || '未分類' }}</span>
          <span class="location-tag">📍 {{ spot.location }}</span>
        </div>

        <div class="card-body">
          <h3>{{ spot.name }}</h3>
          
          <div class="info-row">
            <span>🕒 {{ spot.hours || '全天開放' }}</span>
          </div>

          <div class="tags-row">
            <template v-if="spot.features && spot.features.features">
              <span v-for="(tag, index) in spot.features.features.slice(0, 3)" :key="index" class="feature-tag">
                #{{ tag }}
              </span>
            </template>
          </div>

          <div class="footer">
             <span class="label">推薦：</span>
             <span v-if="spot.activities && spot.activities.activities">
               {{ spot.activities.activities.join('、') }}
             </span>
             <span v-else>自由探索</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* 1. 外層容器 */
.spot-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 2. 標題樣式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--border-color); /* 改用變數 */
  padding-bottom: 10px;
}

.header h2 {
  margin: 0;
  color: var(--text-color); /* 改用變數 */
}

.count {
  color: var(--text-secondary); /* 改用變數 */
  font-size: 0.9rem;
}

.loading {
  text-align: center;
  color: var(--text-secondary); /* 改用變數 */
  font-size: 1.2rem;
  margin-top: 50px;
}

/* 3. 網格排版 */
.grid-layout {
  display: grid;
  grid-template-columns: repeat(4, 1fr); 
  gap: 20px;
}

@media (max-width: 1024px) {
  .grid-layout {
    grid-template-columns: repeat(2, 1fr); /* 平板變 2 欄 */
  }
}

@media (max-width: 768px) {
  .grid-layout {
    grid-template-columns: repeat(1, 1fr); /* 手機變 1 欄 */
  }
}

/* 4. 卡片樣式 */
.card {
  background: var(--card-bg); /* 改用變數 (白/深灰) */
  border: 1px solid var(--border-color); /* 改用變數 */
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 8px var(--shadow-color); /* 改用變數 */
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px var(--shadow-color);
}

/* 5. 圖片區塊 */
.image-box {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.image-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.card:hover .image-box img {
  transform: scale(1.1);
}

.category-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--primary-color);
  font-size: 12px;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 20px;
}

.location-tag {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}

/* 6. 內容區塊 */
.card-body {
  padding: 15px;
}

.card-body h3 {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  color: var(--text-color); /* 改用變數 */
  white-space: nowrap; 
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-row {
  font-size: 12px;
  color: var(--text-secondary); /* 改用變數 */
  margin-bottom: 10px;
}

.tags-row {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap; /* 標籤太多時自動換行 */
}

.feature-tag {
  background: var(--input-bg); /* 改用變數 (淺灰/深灰) */
  color: var(--primary-color);
  border: 1px solid var(--border-color);
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}

.footer {
  border-top: 1px solid var(--border-color); /* 改用變數 */
  padding-top: 10px;
  font-size: 12px;
  color: var(--text-secondary); /* 改用變數 */
}

.label {
  font-weight: bold;
  color: var(--text-color); /* 改用變數 */
}
</style>