<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '../api/axios.js'

const props = defineProps({
  user: Object,
  initialCategory: String
})

const emit = defineEmits(['changePage'])

// --- 狀態變數 ---
const spots = ref([]) // 景點列表
const itineraries = ref([]) // 使用者的行程列表
const loading = ref(true)
const errorMessage = ref('')
const sortBy = ref('newest') 
const selectedCategory = ref('全部') // 預設分類

const showAddModal = ref(false)
const selectedSpotId = ref(null)
const selectedItineraryId = ref('')

// --- 產生隨機圖片網址 ---
const getImageUrl = (id) => `https://picsum.photos/seed/${id}/400/300`

const allCategories = computed(() => {
  const categories = spots.value.map(s => s.category || '未分類')
  return ['全部', ...new Set(categories)]
})

const setCategory = (cat) => {
  selectedCategory.value = cat;
}

// --- 計算屬性：排序與篩選 ---
const sortedSpots = computed(() => {
  let list = [...spots.value]

  if (selectedCategory.value !== '全部') {
    list = list.filter(spot => (spot.category || '未分類') === selectedCategory.value)
  }
  
  if (sortBy.value === 'newest') {
    return list.reverse() 
  } else if (sortBy.value === 'oldest') {
    return list 
  } else if (sortBy.value === 'name_asc') {
    return list.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant')) 
  }
  return list
})

// --- API 方法 ---
const fetchSpots = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    // 假設後端 spots 路由前綴是 /api
    const response = await api.get('/api/spots')
    spots.value = response.data
    
    if (spots.value.length === 0) {
      errorMessage.value = '📭 目前沒有任何景點資料，請點擊右上角新增！'
    }
  } catch (error) {
    console.error("抓不到資料:", error)
    if (error.code === 'ERR_NETWORK') {
      errorMessage.value = '❌ 無法連線到後端伺服器！'
    } else {
      errorMessage.value = `❌ 發生錯誤：${error.message}`
    }
  } finally {
    loading.value = false
  }
}

const fetchUserItineraries = async () => {
    if (!props.user) {
        itineraries.value = [];
        return;
    }
    try {
        const res = await api.get(`/api/itineraries/user/${props.user.id}`);
        itineraries.value = res.data;
    } catch (e) {
        console.error("載入行程失敗", e);
    }
};

const openAddModal = (spotId) => {
    if (!props.user) {
        alert("請先登入才能加入行程！");
        return;
    }
    if (itineraries.value.length === 0) {
        alert("您還沒有建立任何行程，請先去「個人頁面」建立一個行程吧！");
        if (wantToCreate) {
            // 使用者按「確定」，通知 App.vue 跳轉去 User 頁面
            emit('changePage', 'user'); 
        }
        return;
      }
    
    selectedSpotId.value = spotId;
    if (itineraries.value.length > 0) {
        selectedItineraryId.value = itineraries.value[0].id; 
    }
    showAddModal.value = true;
};

const addToItinerary = async () => {
    if (!selectedItineraryId.value) return;
    try {
        await api.post(`/api/itineraries/${selectedItineraryId.value}/add_spot`, {
            spot_id: selectedSpotId.value,
            day: 1 
        });
        alert("🎉 成功加入行程！");
        showAddModal.value = false;
    } catch (e) {
        console.error(e);
        alert("加入失敗，請稍後再試。");
    }
};

onMounted(() => {
  fetchSpots()
  // 如果一開始就有 user (例如重新整理後)，也要抓行程
  if (props.user) fetchUserItineraries()
})

// 監聽 User 變化
watch(() => props.user, (newUser) => {
    if (newUser) fetchUserItineraries();
    else itineraries.value = [];
});
</script>

<template>
  <div class="spot-container">
    
    <div class="header">
      <div class="header-left">
        <h2>🏝️ 熱門景點列表</h2>
        <span class="count" v-if="!errorMessage && !loading">
          共 {{ sortedSpots.length }} 個景點
        </span>
      </div>
      
      <div class="header-right" v-if="!loading && !errorMessage">
        <select v-model="sortBy" class="sort-select">
          <option value="newest">🕒 最新建立</option>
          <option value="oldest">🐢 最舊建立</option>
          <option value="name_asc">🔤 名稱排序</option>
        </select>
      </div>
    </div>

    <div class="category-section" v-if="!loading && !errorMessage">
      <button 
        v-for="cat in allCategories" 
        :key="cat"
        :class="['cat-btn', { active: selectedCategory === cat }]"
        @click="setCategory(cat)"
      >
        {{ cat }}
      </button>
    </div>

    <div v-if="loading" class="state-box loading">
      <span class="spinner">⏳</span> 正在讀取資料...
    </div>

    <div v-else-if="errorMessage" class="state-box error">
      <pre>{{ errorMessage }}</pre>
      <button @click="fetchSpots" class="retry-btn">
        🔄 再試一次
      </button>
    </div>

    <div v-else class="grid-layout">
      <div v-for="spot in sortedSpots" :key="spot.id" class="card">
        
        <div class="image-box">
          <img :src="getImageUrl(spot.id)" alt="景點圖片">
          <span class="category-tag">
            {{ spot.category || '未分類' }}
          </span>
          <span class="location-tag" v-if="spot.location">
            📍 {{ spot.location }}
          </span>
        </div>

        <div class="card-body">
          <h3>{{ spot.name }}</h3>
          
          <div class="info-row">
            <span>🕒 {{ spot.hours || '全天開放' }}</span>
          </div>

          <div class="tags-row">
            <template v-if="spot.features && spot.features.features">
              <span 
                v-for="(tag, index) in spot.features.features.slice(0, 3)" 
                :key="index" 
                class="feature-tag">
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

    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal-content">
        <h3>選擇要加入的行程</h3>
        <p>請選擇您想將此景點加入哪一個行程表：</p>
        
        <select v-model="selectedItineraryId" class="modal-select">
            <option v-for="itin in itineraries" :key="itin.id" :value="itin.id">
                {{ itin.title }}
            </option>
        </select>

        <div class="modal-actions">
            <button @click="addToItinerary" class="btn-confirm">確定加入</button>
            <button @click="showAddModal = false" class="btn-cancel">取消</button>
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

/* 分類按鈕 */
.category-section { margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
.cat-btn { padding: 6px 16px; border: 1px solid #ddd; background: white; border-radius: 20px; cursor: pointer; transition: all 0.3s; }
.cat-btn.active { background-color: #4CAF50; color: white; border-color: #4CAF50; }
.cat-btn:hover:not(.active) { background-color: #f0f0f0; }

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

.footer {
  margin-top: auto;
  border-top: 1px solid #eee;
  padding-top: 10px;
  display: flex;
  justify-content: space-between; /* 左右分開 */
  align-items: center;
}

/* ➕ 按鈕樣式 */
.btn-add-itin {
  background-color: #4CAF50;
  color: white;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%; /* 圓形 */
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: transform 0.2s;
}
.btn-add-itin:hover {
  transform: scale(1.1);
  background-color: #45a049;
}

/* Modal 彈窗樣式 */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); /* 半透明黑底 */
  display: flex; justify-content: center; align-items: center;
  z-index: 9999;
}
.modal-content {
  background: white; padding: 25px; border-radius: 12px;
  width: 90%; max-width: 400px; text-align: center;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.modal-select {
  width: 100%; padding: 10px; margin: 20px 0;
  border-radius: 6px; border: 1px solid #ddd;
}
.modal-actions { display: flex; gap: 10px; justify-content: center; }
.btn-confirm { background: #2ecc71; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; }
.btn-cancel { background: #e74c3c; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; }

/* ... (Grid Layout, Card 等原本樣式請保留) ... */
.grid-layout { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.card { background: white; border: 1px solid #eee; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; }
.image-box { height: 160px; overflow: hidden; position: relative; }
.image-box img { width: 100%; height: 100%; object-fit: cover; }
.card-body { padding: 15px; flex: 1; display: flex; flex-direction: column; }
</style>