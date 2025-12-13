<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// --- 狀態變數 ---
const spots = ref([])
const loading = ref(true)
const errorMessage = ref('')
const sortBy = ref('newest') // 預設排序：最新

// --- 產生隨機圖片網址 (使用 id 當種子) ---
const getImageUrl = (id) => {
  return `https://picsum.photos/seed/${id}/400/300`
}

// --- 計算屬性：處理排序邏輯 ---
const sortedSpots = computed(() => {
  // 1. 複製一份陣列，避免直接修改原始資料 (Vue 最佳實踐)
  const list = [...spots.value]
  
  // 2. 根據 sortBy 的值進行排序
  if (sortBy.value === 'newest') {
    // 假設後端回傳預設是舊到新 (id 小到大)，反轉就是最新
    // 如果後端有 created_at 欄位，建議改用日期排序會更準確
    return list.reverse() 
  } else if (sortBy.value === 'oldest') {
    return list // 原始順序
  } else if (sortBy.value === 'name_asc') {
    // 中文筆畫排序 (localeCompare)
    return list.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant')) 
  }
  
  return list
})

// --- 抓取資料 ---
const fetchSpots = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    // 呼叫後端 API
    const response = await axios.get('http://127.0.0.1:8000/spots')
    spots.value = response.data
    
    // 如果資料庫是空的
    if (spots.value.length === 0) {
      errorMessage.value = '📭 目前沒有任何景點資料，請點擊右上角新增！'
    }
  } catch (error) {
    console.error("抓不到資料:", error)
    
    // 判斷錯誤類型，給予使用者友善的提示
    if (error.code === 'ERR_NETWORK') {
      errorMessage.value = '❌ 無法連線到後端伺服器！請確認終端機是否已執行 uvicorn。'
    } else if (error.response && error.response.status === 404) {
      errorMessage.value = '❌ 找不到 API 路徑 (404)！'
    } else {
      errorMessage.value = `❌ 發生未預期的錯誤：${error.message}`
    }
  } finally {
    // 無論成功失敗，最後都要關閉載入動畫
    loading.value = false
  }
}

// --- 生命週期：元件掛載時自動抓取 ---
onMounted(() => {
  fetchSpots()
})
</script>

<template>
  <div class="spot-container">
    
    <div class="header">
      <div class="header-left">
        <h2>🏝️ 熱門景點列表</h2>
        <span class="count" v-if="!errorMessage && !loading">共 {{ spots.length }} 個景點</span>
      </div>
      
      <div class="header-right" v-if="!loading && !errorMessage">
        <select v-model="sortBy" class="sort-select">
          <option value="newest">🕒 最新建立</option>
          <option value="oldest">🐢 最舊建立</option>
          <option value="name_asc">🔤 名稱排序</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="state-box loading">
      <span class="spinner">⏳</span> 正在讀取資料...
    </div>

    <div v-else-if="errorMessage" class="state-box error">
      <pre>{{ errorMessage }}</pre>
      <button @click="fetchSpots" class="retry-btn">🔄 再試一次</button>
    </div>

    <div v-else class="grid-layout">
      <div v-for="spot in sortedSpots" :key="spot.id" class="card">
        
        <div class="image-box">
          <img :src="getImageUrl(spot.id)" alt="景點圖片">
          <span class="category-tag">{{ spot.category || '未分類' }}</span>
          <span class="location-tag" v-if="spot.location">📍 {{ spot.location }}</span>
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

/* Header 排版 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--border-color, #eee);
  padding-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.header-left h2 { margin: 0; color: var(--text-color, #333); display: inline-block; margin-right: 10px;}
.count { color: var(--text-secondary, #666); font-size: 0.9rem; }

/* 排序選單 */
.sort-select {
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid var(--input-border, #ddd);
  background-color: var(--card-bg, #fff);
  color: var(--text-color, #333);
  font-size: 0.9rem;
  cursor: pointer;
  outline: none;
}
.sort-select:hover { border-color: var(--primary-color, #4CAF50); }

/* 狀態訊息 (Loading / Error) */
.state-box {
  text-align: center;
  padding: 40px;
  background-color: var(--card-bg, #fff);
  border-radius: 12px;
  border: 1px solid var(--border-color, #eee);
  margin-top: 20px;
}

.loading { color: var(--text-secondary, #666); font-size: 1.2rem; }
.spinner { display: inline-block; animation: spin 2s linear infinite; margin-right: 10px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.error { color: #e74c3c; background-color: #fff2f0; border-color: #ffccc7; }
.retry-btn {
  margin-top: 15px; padding: 8px 16px; background-color: var(--primary-color, #4CAF50);
  color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem;
}
.retry-btn:hover { opacity: 0.9; }

/* 網格系統 RWD */
.grid-layout {
  display: grid;
  grid-template-columns: repeat(4, 1fr); 
  gap: 20px;
}
@media (max-width: 1024px) { .grid-layout { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .grid-layout { grid-template-columns: repeat(1, 1fr); } }

/* 卡片樣式 */
.card {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #eee);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 8px var(--shadow-color, rgba(0,0,0,0.05));
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  display: flex;
  flex-direction: column; /* 讓內容上下排列 */
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px var(--shadow-color, rgba(0,0,0,0.1));
}

.image-box { position: relative; height: 160px; overflow: hidden; }
.image-box img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
.card:hover .image-box img { transform: scale(1.1); }

.category-tag {
  position: absolute; top: 10px; left: 10px;
  background: rgba(255, 255, 255, 0.9); color: var(--primary-color, #4CAF50);
  font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 20px;
}
.location-tag {
  position: absolute; bottom: 10px; right: 10px;
  background: rgba(0, 0, 0, 0.6); color: white;
  font-size: 12px; padding: 4px 8px; border-radius: 4px;
}

.card-body { padding: 15px; flex: 1; display: flex; flex-direction: column; }
.card-body h3 {
  margin: 0 0 10px 0; font-size: 1.1rem; color: var(--text-color, #333);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.info-row { font-size: 12px; color: var(--text-secondary, #666); margin-bottom: 10px; }
.tags-row { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
.feature-tag {
  background: var(--input-bg, #f9f9f9); color: var(--primary-color, #4CAF50);
  border: 1px solid var(--border-color, #eee); font-size: 11px; padding: 2px 6px; border-radius: 4px;
}
.footer {
  margin-top: auto; /* 將 footer 推到底部 */
  border-top: 1px solid var(--border-color, #eee); padding-top: 10px;
  font-size: 12px; color: var(--text-secondary, #666);
}
.label { font-weight: bold; color: var(--text-color, #333); }
</style>