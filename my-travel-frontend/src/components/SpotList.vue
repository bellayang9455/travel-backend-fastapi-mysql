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
/* 1. 外層容器：給一點內距 */
.spot-container {
  padding: 20px;
  max-width: 1200px; /* 限制最大寬度，避免螢幕太大時拉太長 */
  margin: 0 auto;    /* 置中 */
}

/* 2. 標題樣式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.count {
  color: #888;
  font-size: 0.9rem;
}

/* 3. 網格排版 */
.grid-layout {
  display: grid;
  /* 強制分成 4 欄，每一欄寬度一樣 (1fr) */
  grid-template-columns: repeat(4, 1fr); 
  gap: 20px; /* 卡片之間的距離 */
}

/* 如果螢幕真的太小 (手機)，還是要變直的比較好看，不然會擠爆 */
@media (max-width: 768px) {
  .grid-layout {
    grid-template-columns: repeat(1, 1fr); /* 手機變 1 欄 */
  }
}

/* 4. 卡片樣式 */
.card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 12px; /* 圓角 */
  overflow: hidden; /* 讓圖片不凸出去 */
  box-shadow: 0 4px 8px rgba(0,0,0,0.05); /* 淡淡陰影 */
  transition: transform 0.2s; /* 動畫 */
  cursor: pointer;
}

.card:hover {
  transform: translateY(-5px); /* 滑鼠移上去浮起來 */
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

/* 5. 圖片區塊 */
.image-box {
  position: relative;
  height: 160px; /* ⭐ 固定高度，這樣圖片就不會忽大忽小 ⭐ */
  overflow: hidden;
}

.image-box img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 裁切圖片填滿，不變形 */
  transition: transform 0.5s;
}

.card:hover .image-box img {
  transform: scale(1.1); /* 圖片放大特效 */
}

/* 圖片上的標籤 */
.category-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: #007bff;
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
  color: #333;
  white-space: nowrap; /* 不換行 */
  overflow: hidden;
  text-overflow: ellipsis; /* 太長變... */
}

.info-row {
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.tags-row {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
}

.feature-tag {
  background: #eef;
  color: #007bff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}

.footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
  font-size: 12px;
  color: #666;
}

.label {
  font-weight: bold;
  color: #555;
}
</style>