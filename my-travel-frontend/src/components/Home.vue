<script setup>
// 首頁景點列表
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter,useRoute } from 'vue-router';
import api from '../api/axios.js'
import SpotForm from './SpotForm.vue'

// 接收 App.vue 傳來的 user
const props = defineProps({
  user: Object,
  initialCategory: String
})
const route = useRoute();
const router = useRouter();

// 狀態變數
const spots = ref([])
const itineraries = ref([]) // 使用者的行程列表
const loading = ref(true)
const errorMessage = ref('')
const sortBy = ref('newest') // 預設排序
const selectedCategory = ref(props.initialCategory || '全部')//景點分類預設全部

// 彈出視窗控制
const showAddModal = ref(false)
const selectedSpotId = ref(null)
const selectedItineraryId = ref('')

// 編輯功能
const showEditModal = ref(false)
const currentEditSpot = ref(null)

// 產生隨機圖片網址
const getImageUrl = (id) => {
  // 使用 picsum，id 當種子確保圖片固定
  return `https://picsum.photos/seed/${id}/400/300`
}

// 計算屬性：取得所有分類
const allCategories = computed(() => {
  // 1. 取得所有景點的分類
  const categories = spots.value.map(s => s.category || '未分類')
  // 2. 使用 Set 去除重複，並在最前面加上 '全部'
  return ['全部', ...new Set(categories)]
})

// 計算屬性：排序邏輯
const sortedSpots = computed(() => {
  let list = [...spots.value]

  //景點分類篩選
  if (selectedCategory.value !== '全部') {
    list = list.filter(spot => {
       const cat = spot.category || '未分類';
       // 讓 '🛍️ 購物商圈' 也能被 '購物商圈' 找到
       return cat.includes(selectedCategory.value);
    })
  }

  //洲際別篩選
  if (route.query.location) {
    list = list.filter(spot => {
      console.log(`比對景點 ${spot.name}，它的 region 是：${spot.region}`);
      return spot.region === route.query.location
    })
  }
 
// 依時間排序
 if (sortBy.value === 'newest') {
    // 最新建立：時間越晚的排越前面 (b - a)
    return list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    
  } else if (sortBy.value === 'oldest') {
    // 最舊建立：時間越早的排越前面 (a - b)
    return list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    
  } else if (sortBy.value === 'name_asc') {
    // 名稱排序保持不變
    return list.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant')) 
  }
  return list
})

// API 方法

// 1. 抓取景點
const fetchSpots = async (keyword = '') => {
  loading.value = true
  errorMessage.value = ''
  try {
    // 帶上 query 參數 q
    const response = await api.get(`/api/spots`, {
        params: { q: keyword }
    })
    spots.value = response.data

    console.log("🔍 API 傳來的第一筆景點長這樣：", spots.value[0])
    
    if (spots.value.length === 0) {
      if (keyword) {
          errorMessage.value = `🔍 找不到與「${keyword}」相關的景點，試試別的關鍵字？`
      } else {
          errorMessage.value = '📭 目前沒有任何景點資料，請點擊右上角新增！'
      }
    }
  } catch (error) {
    console.error("抓不到資料:", error)
    if (error.code === 'ERR_NETWORK') {
      errorMessage.value = '❌ 無法連線到後端！請確認 uvicorn 是否已執行。'
    } else {
      errorMessage.value = `❌ 發生錯誤：${error.message}`
    }
  } finally {
    loading.value = false
  }
}

// 2. 抓取使用者行程 (為了下拉選單)
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

// 3. 開啟加入視窗
const openAddModal = (spotId) => {
    if (!props.user) {
        alert("請先登入才能加入行程！");
        return;
    }
    if (itineraries.value.length === 0) {
        alert("您還沒有建立任何行程，請先去「個人頁面」建立一個行程吧！");
        return;
    }
    selectedSpotId.value = spotId;
    // 預設選第一個行程
    if (itineraries.value.length > 0) {
        selectedItineraryId.value = itineraries.value[0].id; 
    }
    showAddModal.value = true;
};

// 4. 送出加入請求
const addToItinerary = async () => {
    if (!selectedItineraryId.value) return;
    try {
        await api.post(`/api/itineraries/${selectedItineraryId.value}/add_spot`, {
            spot_id: selectedSpotId.value
        });
        alert("🎉 成功加入行程！");
        showAddModal.value = false;
    } catch (e) {
        console.error(e);
        alert("加入失敗，請檢查後端連線。");
    }
};

// 生命週期與監聽
onMounted(() => {
  fetchSpots(route.query.q || '')
  
  if (props.user) fetchUserItineraries()
})

// 監聽網址變化
watch(
  () => route.query.q,
  (newKeyword) => {
    // 如果搜尋關鍵字變了 (包含變回空字串)，就重新抓取
    fetchSpots(newKeyword || '')
    // 搜尋時建議把分類重置為全部，避免使用者以為沒搜到 (可選)
    selectedCategory.value = '全部' 
  }
)

// 監聽 initialCategory 變化
watch(() => props.initialCategory, (newVal) => {
    if (newVal) {
        selectedCategory.value = newVal;

        const matchCount = spots.value.filter(s => s.category === newVal).length;
        console.log(`資料庫裡分類是「${newVal}」的共有: ${matchCount} 筆`);
    }
});

// 監聽 user 變化 (例如剛登入)
watch(() => props.user, (newUser) => {
    if (newUser) fetchUserItineraries();
    else itineraries.value = [];
});

const clearSearch = () => {
    router.push({ name: 'home' }) // 這會清空網址參數，觸發上面的 watch
}

// 開啟編輯視窗
const openEditModal = (spot) => {
  console.log("✏️ 準備編輯這筆資料：", spot)
  currentEditSpot.value = spot
  showEditModal.value = true
}

// 編輯成功後的處理
const handleEditSuccess = () => {
  showEditModal.value = false
  currentEditSpot.value = null
  fetchSpots() // 重新拉取最新的景點列表來更新畫面！
}
</script>

<template>
  <div class="spot-container">
    <div class="header">
      <div class="header-left">
        <h2>🏝️ 熱門景點列表</h2>
        <span class="category-badge" v-if="selectedCategory !== '全部'">
          {{ selectedCategory }}
        </span>
        <span class="count" v-if="!errorMessage && !loading">共 {{ sortedSpots.length }} 個景點</span>
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
          <div class="title-row">
              <h3>{{ spot.name }}</h3>
          </div>
          
          <div class="info-row">
            <span>🕒 {{ spot.hours || '全天開放' }}</span>
          </div>

          <div class="tags-row">
            <template v-if="spot.features?.features?.length > 0 && spot.features.features[0] !== ''">
              <span v-for="(tag, index) in spot.features.features.slice(0, 3)" :key="index" class="feature-tag">
                #{{ tag }}
              </span>
            </template>
          </div>

          <div class="footer">
             <div class="rec-text">
                 <span class="label">推薦：</span>
                 <span v-if="spot.activities?.activities?.length > 0 && spot.activities.activities[0] !== ''">
                   {{ spot.activities.activities.slice(0, 2).join('、') }}
                 </span>
                 <span v-else>自由探索</span>
             </div>
             
             <button @click.stop="openEditModal(spot)" class="btn-add-itin" style="background-color: #f39c12; margin-right: 5px;" title="編輯景點">
               ✏️
             </button>
             
             <button @click.stop="openAddModal(spot.id)" class="btn-add-itin" title="加入行程">
               📅
             </button>
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

    <div v-if="showEditModal" class="modal-overlay" style="z-index: 9999;">
      <div style="width: 90%; max-width: 800px; max-height: 90vh; overflow-y: auto;">
         <SpotForm 
           :spotToEdit="currentEditSpot" 
           @submitSuccess="handleEditSuccess" 
           @cancel="showEditModal = false" 
         />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 保留您原本的所有樣式 */
.spot-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid var(--border-color, #eee); padding-bottom: 15px; flex-wrap: wrap; gap: 10px; }
.header-left h2 { margin: 0; color: var(--text-color, #333); display: inline-block; margin-right: 10px;}
.count { color: var(--text-secondary, #666); font-size: 0.9rem; }
.sort-select { padding: 8px 12px; border-radius: 20px; border: 1px solid var(--input-border, #ddd); background-color: var(--card-bg, #fff); color: var(--text-color, #333); font-size: 0.9rem; cursor: pointer; outline: none; }
.state-box { text-align: center; padding: 40px; background-color: var(--card-bg, #fff); border-radius: 12px; border: 1px solid var(--border-color, #eee); margin-top: 20px; }
.loading { color: var(--text-secondary, #666); font-size: 1.2rem; }
.spinner { display: inline-block; animation: spin 2s linear infinite; margin-right: 10px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.error { color: #e74c3c; background-color: #fff2f0; border-color: #ffccc7; }
.retry-btn { margin-top: 15px; padding: 8px 16px; background-color: var(--primary-color, #4CAF50); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; }
.grid-layout { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
@media (max-width: 1024px) { .grid-layout { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .grid-layout { grid-template-columns: repeat(1, 1fr); } }
.category-badge {
  background-color: var(--primary-color);
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  margin-right: 10px;
  display: inline-block;
}
/* 卡片與內容 */
.card { background: var(--card-bg, #fff); border: 1px solid var(--border-color, #eee); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 8px var(--shadow-color, rgba(0,0,0,0.05)); transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; display: flex; flex-direction: column; }
.card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px var(--shadow-color, rgba(0,0,0,0.1)); }
.image-box { position: relative; height: 160px; overflow: hidden; }
.image-box img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
.card:hover .image-box img { transform: scale(1.1); }
.category-tag { position: absolute; top: 10px; left: 10px; background: rgba(255, 255, 255, 0.9); color: var(--primary-color, #4CAF50); font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 20px; }
.location-tag { position: absolute; bottom: 10px; right: 10px; background: rgba(0, 0, 0, 0.6); color: white; font-size: 12px; padding: 4px 8px; border-radius: 4px; }
.card-body { padding: 15px; flex: 1; display: flex; flex-direction: column; }
.card-body h3 { margin: 0 0 10px 0; font-size: 1.1rem; color: var(--text-color, #333); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.info-row { font-size: 12px; color: var(--text-secondary, #666); margin-bottom: 10px; }
.tags-row { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
.feature-tag { background: var(--input-bg, #f9f9f9); color: var(--primary-color, #4CAF50); border: 1px solid var(--border-color, #eee); font-size: 11px; padding: 2px 6px; border-radius: 4px; }

/* Footer 修改：讓按鈕與文字並排 */
.footer { margin-top: auto; border-top: 1px solid var(--border-color, #eee); padding-top: 10px; font-size: 12px; color: var(--text-secondary, #666); display: flex; justify-content: space-between; align-items: center; }
.rec-text { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.label { font-weight: bold; color: var(--text-color, #333); }

/* ⭐ 新增：加入行程按鈕樣式 */
.btn-add-itin { background-color: var(--primary-color, #4CAF50); color: white; border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; transition: background 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.btn-add-itin:hover { background-color: #45a049; transform: scale(1.1); }

/* ⭐ 新增：Modal 樣式 */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 9999; }
.modal-content { background: var(--card-bg, white); padding: 25px; border-radius: 12px; width: 90%; max-width: 400px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.3); color: var(--text-color, #333); }
.modal-select { width: 100%; padding: 10px; margin: 20px 0; border-radius: 6px; border: 1px solid var(--border-color, #ccc); font-size: 1rem; background: var(--input-bg, #fff); color: var(--text-color, #333); }
.modal-actions { display: flex; gap: 10px; justify-content: center; }
.btn-confirm { background: #2ecc71; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.btn-cancel { background: #e74c3c; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
</style>
