<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const spots = ref([])
const loading = ref(true)
const errorMessage = ref('')
const sortBy = ref('newest') // ⭐ 新增：排序狀態 (預設最新)

const getImageUrl = (id) => {
  return `https://picsum.photos/seed/${id}/400/300`
}

// ⭐ 新增：排序邏輯
const sortedSpots = computed(() => {
  // 複製一份陣列以免改到原始資料
  const list = [...spots.value]
  
  if (sortBy.value === 'newest') {
    // 假設 id 越大越新，或是之後有 created_at 可以改用日期排
    return list.reverse() 
  } else if (sortBy.value === 'oldest') {
    return list // 預設就是舊到新
  } else if (sortBy.value === 'name_asc') {
    return list.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant')) // 中文筆畫排序
  }
  
  return list
})

const fetchSpots = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await axios.get('http://127.0.0.1:8000/spots')
    spots.value = response.data
    
    if (spots.value.length === 0) {
      errorMessage.value = '📭 資料庫目前沒有任何景點資料，請先新增！'
    }
  } catch (error) {
    console.error("抓不到資料:", error)
    if (error.code === 'ERR_NETWORK') {
      errorMessage.value = '❌ 無法連線到後端伺服器！請確認後端是否開啟。'
    } else if (error.response && error.response.status === 404) {
      errorMessage.value = '❌ 找不到 API 路徑 (404)！'
    } else {
      errorMessage.value = `❌ 發生錯誤：${error.message}`
    }
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
      <div class="header-left">
        <h2>🏝️ 熱門景點列表</h2>
        <span class="count" v-if="!errorMessage">共 {{ spots.length }} 個景點</span>
      </div>
      
      <!-- ⭐ 新增：排序控制項 -->
      <div class="header-right" v-if="!loading && !errorMessage">
        <select v-model="sortBy" class="sort-select">
          <option value="newest">🕒 最新建立</option>
          <option value="oldest">🐢 最舊建立</option>
          <option value="name_asc">🔤 名稱排序</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="state-box loading">
      <span class="spinner">⏳</span> 正在讀取資料庫...
    </div>

    <div v-else-if="errorMessage" class="state-box error">
      <pre>{{ errorMessage }}</pre>
      <button @click="fetchSpots" class="retry-btn">🔄 再試一次</button>
    </div>

    <!-- ⭐ 修改：使用 sortedSpots 進行迴圈 -->
    <div v-else class="grid-layout">
      <div v-for="spot in sortedSpots" :key="spot.id" class="card">
        
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
.spot-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header 排版調整 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 15px;
  flex-wrap: wrap; /* 手機版自動換行 */
  gap: 10px;
}

.header-left h2 { margin: 0; color: var(--text-color); display: inline-block; margin-right: 10px;}
.count { color: var(--text-secondary); font-size: 0.9rem; }

/* 排序選單樣式 */
.sort-select {
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid var(--input-border);
  background-color: var(--card-bg);
  color: var(--text-color);
  font-size: 0.9rem;
  cursor: pointer;
  outline: none;
}
.sort-select:hover { border-color: var(--primary-color); }

/* 狀態訊息樣式 */
.state-box {
  text-align: center;
  padding: 40px;
  background-color: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-top: 20px;
}

.loading { color: var(--text-secondary); font-size: 1.2rem; }
.spinner { display: inline-block; animation: spin 2s linear infinite; margin-right: 10px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.error { color: #e74c3c; background-color: #fff2f0; border-color: #ffccc7; }
.retry-btn {
  margin-top: 15px; padding: 8px 16px; background-color: var(--primary-color);
  color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem;
}
.retry-btn:hover { opacity: 0.9; }

/* 網格排版 */
.grid-layout {
  display: grid;
  grid-template-columns: repeat(4, 1fr); 
  gap: 20px;
}

@media (max-width: 1024px) { .grid-layout { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .grid-layout { grid-template-columns: repeat(1, 1fr); } }

/* 卡片樣式 */
.card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 8px var(--shadow-color);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px var(--shadow-color);
}

.image-box { position: relative; height: 160px; overflow: hidden; }
.image-box img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
.card:hover .image-box img { transform: scale(1.1); }

.category-tag {
  position: absolute; top: 10px; left: 10px;
  background: rgba(255, 255, 255, 0.9); color: var(--primary-color);
  font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 20px;
}
.location-tag {
  position: absolute; bottom: 10px; right: 10px;
  background: rgba(0, 0, 0, 0.6); color: white;
  font-size: 12px; padding: 4px 8px; border-radius: 4px;
}

.card-body { padding: 15px; }
.card-body h3 {
  margin: 0 0 10px 0; font-size: 1.1rem; color: var(--text-color);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.info-row { font-size: 12px; color: var(--text-secondary); margin-bottom: 10px; }
.tags-row { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
.feature-tag {
  background: var(--input-bg); color: var(--primary-color);
  border: 1px solid var(--border-color); font-size: 11px; padding: 2px 6px; border-radius: 4px;
}
.footer {
  border-top: 1px solid var(--border-color); padding-top: 10px;
  font-size: 12px; color: var(--text-secondary);
}
.label { font-weight: bold; color: var(--text-color); }
</style>