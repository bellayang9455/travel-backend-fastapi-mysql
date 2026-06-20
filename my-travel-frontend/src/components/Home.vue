<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router';
import api from '../api/axios.js'
import SpotForm from './SpotForm.vue'
import ReviewSection from '../components/ReviewSection.vue'; 

// 變數與函式定義
const props = defineProps({
  user: Object,
  initialCategory: String
})
const route = useRoute();
const router = useRouter();

const spots = ref([])
const itineraries = ref([])
const loading = ref(true)
const errorMessage = ref('')
const sortBy = ref('newest')
const selectedCategory = ref(props.initialCategory || '全部')
const searchQuery = ref(route.query.q || '')

const showDetailModal = ref(false)
const currentDetailSpot = ref(null)

const openDetailModal = (spot) => {
  currentDetailSpot.value = spot
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  currentDetailSpot.value = null
}

const showAddModal = ref(false)
const selectedSpotId = ref(null)
const selectedItineraryId = ref('')
const showEditModal = ref(false)
const currentEditSpot = ref(null)

// ✨ 動態莫蘭迪質感漸層背景渲染 (對應 Navbar 的七大類別)
const getBgStyle = (category) => {
  const gradients = {
    '自然生態': 'linear-gradient(135deg, #065f46 0%, #064e3b 100%)', // 深夜翡翠
    '歷史人文': 'linear-gradient(135deg, #1e40af 0%, #172554 100%)', // 皇家午夜藍
    '在地美食': 'linear-gradient(135deg, #991b1b 0%, #450a0a 100%)', // 勃根地酒紅
    '休閒娛樂': 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)', // 湖水湛藍
    '購物商圈': 'linear-gradient(135deg, #c026d3 0%, #86198f 100%)', // 霓虹紫羅蘭
    '網美打卡': 'linear-gradient(135deg, #be123c 0%, #881337 100%)', // 玫瑰胭脂
    '其他': 'linear-gradient(135deg, #475569 0%, #1e293b 100%)',     // 曜石板灰
  }
  return { background: gradients[category] || 'linear-gradient(135deg, #334155 0%, #0f172a 100%)' }; // 預設深灰
}

const sortedSpots = computed(() => {
  let list = [...spots.value]
  console.log('🟦 原始 spots 數量:', list.length, '搜尋詞 q:', route.query.q)

  if (selectedCategory.value !== '全部') {
    console.log('🟨 套用分類篩選:', selectedCategory.value)
    list = list.filter(spot => (spot.category || '未分類').includes(selectedCategory.value))
    console.log('🟨 分類篩選後剩餘:', list.length)
  }

  if (route.query.location) {
    console.log('🟧 套用地點篩選:', route.query.location)
    list = list.filter(spot => spot.region === route.query.location)
    console.log('🟧 地點篩選後剩餘:', list.length)
  }

  console.log('✅ 最終顯示數量:', list.length)

  if (sortBy.value === 'newest') return list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  if (sortBy.value === 'oldest') return list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  if (sortBy.value === 'name_asc') return list.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant'))
  return list
})

const handleSearch = () => {
  router.push({ query: { ...route.query, q: searchQuery.value } })
}

const fetchSpots = async (keyword) => {
  const searchK = (typeof keyword === 'string') ? keyword : (route.query.q || '');
  loading.value = true
  try {
    const response = await api.get(`/api/spots/`, { params: { q: searchK } })
    spots.value = response.data
    if (showDetailModal.value && currentDetailSpot.value) {
      const updatedSpot = spots.value.find(s => s.id === currentDetailSpot.value.id)
      if (updatedSpot) currentDetailSpot.value = updatedSpot
    }
  } catch (error) {
    errorMessage.value = `❌ 發生錯誤：${error.message}`
  } finally {
    loading.value = false
  }
}

const fetchUserItineraries = async () => {
  if (!props.user) return;
  try {
    const res = await api.get(`/api/itineraries/user/${props.user.id}`);
    itineraries.value = res.data;
  } catch (e) { console.error(e); }
};

// Toast 提示系統
const toastMessage = ref('')
const showToast = (msg) => {
  toastMessage.value = msg
  setTimeout(() => { toastMessage.value = '' }, 3000)
}

const openAddModal = (spotId) => {
  if (!props.user) return showToast("🔒 請先登入！");
  selectedSpotId.value = spotId;
  if (itineraries.value.length > 0) selectedItineraryId.value = itineraries.value[0].id;
  showAddModal.value = true;
};

const addToItinerary = async () => {
  try {
    await api.post(`/api/itineraries/${selectedItineraryId.value}/add_spot`, { spot_id: selectedSpotId.value });
    showToast("🎉 成功加入行程！");
    showAddModal.value = false;
  } catch (e) { showToast("❌ 加入失敗"); }
};

const openEditModal = (spot) => {
  currentEditSpot.value = spot
  showEditModal.value = true
}

const handleEditSuccess = () => {
  showEditModal.value = false
  fetchSpots()
}

onMounted(() => {
  fetchSpots(route.query.q || '')
  searchQuery.value = route.query.q || ''
  if (props.user) fetchUserItineraries()
})

watch(() => route.query.q, (newK) => {
  fetchSpots(newK || '')
  searchQuery.value = newK || ''
})

watch(() => props.user, (newUser) => {
  if (newUser) fetchUserItineraries();
  else itineraries.value = [];
});
</script>

<template>
<div class="home-page">

  <!-- 全域 Toast 提示 -->
  <div v-if="toastMessage" class="toast-notification">
    {{ toastMessage }}
  </div>

  <div class="hero-section">
    <div class="hero-content">
      <h1 class="hero-title">探索你的下一趟完美旅程</h1>
      <div class="search-card">
        <div class="search-tabs">
          <span class="active">
            🔍 找景點
          </span>
        </div>
        <div class="search-inputs">
          <input type="text" placeholder="你想去哪裡？ (例如：台北、東京)" v-model="searchQuery" @keyup.enter="handleSearch" />
          <button class="btn-primary search-btn" @click="handleSearch">搜尋</button>
        </div>
      </div>
    </div>
  </div>

  <div class="spot-container">
    <div class="header">
      <div class="header-left">
        <h2>
          🌴 熱門景點列表
        </h2>
        <span class="category-badge" v-if="selectedCategory !== '全部'">{{ selectedCategory }}</span>
        <span class="count" v-if="!errorMessage && !loading">共 {{ sortedSpots.length }} 個景點</span>
      </div>
      <div class="header-right" v-if="!loading && !errorMessage">
        <select v-model="sortBy" class="sort-select">
          <option value="newest">最新建立</option>
          <option value="oldest">最舊建立</option>
          <option value="name_asc">名稱排序</option>
        </select>
      </div>
    </div>

    <!-- ☠️ 骨架屏 Skeleton Loading (取代原本乾巴巴的轉圈圈) -->
    <div v-if="loading" class="grid-layout">
      <div v-for="n in 8" :key="n" class="spot-card skeleton-card">
        <div class="skeleton-img"></div>
        <div class="card-body">
          <div class="skeleton-title"></div>
          <div class="skeleton-title short"></div>
          
          <div class="skeleton-text mt-4"></div>
          
          <div class="skeleton-tags">
            <div class="skeleton-tag"></div>
            <div class="skeleton-tag"></div>
            <div class="skeleton-tag"></div>
          </div>
          
          <div class="footer skeleton-footer">
            <div class="skeleton-text block"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 錯誤提示 -->
    <div v-else-if="errorMessage" class="state-box error">
      ⚠️ <pre>{{ errorMessage }}</pre>
      <button @click="fetchSpots" class="retry-btn">
        🔄 再試一次
      </button>
    </div>

    <!-- 真實資料呈現區 -->
    <div v-else class="grid-layout">
      <div
        v-for="spot in sortedSpots"
        :key="spot.id"
        class="spot-card"
        @click="openDetailModal(spot)"
      >
        <!-- 圖片區改為動態漸層色塊與大標題 -->
        <div class="image-box dynamic-color-box" :style="getBgStyle(spot.category)">
          <!-- 景點名稱大字 -->
          <div class="spot-title-overlay">{{ spot.name }}</div>

          <span class="category-tag">{{ spot.category || '未分類' }}</span>
          
          <span class="location-tag" v-if="spot.location">
            📍 {{ spot.location }}
          </span>

          <div v-if="(spot.review_count || 0) >= 3" class="img-rating-badge">
            ⭐ {{ spot.avg_rating }}
          </div>
        </div>
        
        <div class="card-body">
          <!-- ✨ 鎖定標題高度，確保排版不因字數而高低起伏 -->
          <div class="title-row">
            <h3 class="spot-name">{{ spot.name }}</h3>
            <div v-if="(spot.review_count || 0) < 3" class="insufficient-badge">人數不足</div>
          </div>
          
          <div class="info-row">
            <span class="info-item">
              🕒 {{ spot.hours || '全天開放' }}
            </span>
            <span class="dot-separator">•</span>
            <span class="info-item">
              💬 {{ spot.review_count || 0 }} 則評論
            </span>
          </div>
          
          <div class="tags-row">
            <template v-if="spot.features?.features?.length > 0 && spot.features.features[0] !== ''">
              <span v-for="(tag, index) in spot.features.features.slice(0, 3)" :key="index" class="feature-tag">#{{ tag }}</span>
            </template>
          </div>
          
          <!-- ✨ 使用 Flexbox 確保底部 Emoji 與文字絕對垂直置中，並鎖定 60px 高度 -->
          <div class="footer">
            <div class="rec-text">
              <span class="label">💡 推薦：</span>
              <span class="rec-content">{{ spot.activities?.activities?.slice(0, 3).join('、') || '自由探索' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal (詳細資訊與評論彈窗) -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="detail-modal-card">
        <button class="modal-close-btn" @click="closeDetailModal">✕</button>
        <div class="detail-layout">
          <!-- 左側：詳細資訊 -->
          <div class="detail-info-side">
            <!-- 彈窗頂部大圖也同步改為動態漸層色塊與大標題 -->
            <div class="detail-image-box dynamic-color-box" :style="getBgStyle(currentDetailSpot.category)">
              <div class="spot-title-overlay modal-title-overlay">{{ currentDetailSpot.name }}</div>

              <div class="detail-img-overlay">
                <span class="detail-category">{{ currentDetailSpot.category || '未分類' }}</span>
              </div>
            </div>
            <div class="detail-content">
              <h2>{{ currentDetailSpot.name }}</h2>
              
              <p class="detail-location">
                📍 {{ currentDetailSpot.location }}
              </p>
              
              <div class="detail-meta">
                <div class="meta-item">
                  <span class="icon">🕒</span>
                  <div class="text">
                    <strong>營業時間</strong>
                    <span>{{ currentDetailSpot.hours || '全天開放' }}</span>
                  </div>
                </div>
                <div class="meta-item">
                  <span class="icon">⭐</span>
                  <div class="text">
                    <strong>評價分數</strong>
                    <span>{{ currentDetailSpot.avg_rating ? `${currentDetailSpot.avg_rating} / 5.0` : '尚無足夠評價' }}</span>
                  </div>
                </div>
              </div>
              
              <div class="detail-tags-section" v-if="currentDetailSpot.features?.features?.length > 0 && currentDetailSpot.features.features[0] !== ''">
                <h4>特色標籤</h4>
                <div class="detail-tags">
                  <span v-for="(tag, index) in currentDetailSpot.features.features" :key="index" class="tag">#{{ tag }}</span>
                </div>
              </div>
              
              <div class="detail-tags-section" v-if="currentDetailSpot.activities?.activities?.length > 0 && currentDetailSpot.activities.activities[0] !== ''">
                <h4>推薦活動</h4>
                <div class="detail-tags">
                  <span v-for="(act, index) in currentDetailSpot.activities.activities" :key="index" class="act-tag">{{ act }}</span>
                </div>
              </div>
              
              <div class="detail-actions">
                <button @click="openEditModal(currentDetailSpot)" class="btn-action btn-edit">
                  ✏️ 編輯資訊
                </button>
                <button @click="openAddModal(currentDetailSpot.id)" class="btn-action btn-add">
                  📅 加入我的行程
                </button>
              </div>
            </div>
          </div>
          <!-- 右側：評論 -->
          <div class="detail-review-side">
            <ReviewSection
              :spotId="currentDetailSpot.id"
              :user="props.user"
              @submitSuccess="fetchSpots"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 加入行程 Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content">
        <h3>選擇要加入的行程</h3>
        <select v-model="selectedItineraryId" class="modal-select">
          <option v-for="itin in itineraries" :key="itin.id" :value="itin.id">{{ itin.title }}</option>
        </select>
        <div class="modal-actions">
          <button @click="addToItinerary" class="btn-confirm">確定加入</button>
          <button @click="showAddModal = false" class="btn-cancel">取消</button>
        </div>
      </div>
    </div>

    <!-- 編輯 Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-inner">
        <SpotForm :spotToEdit="currentEditSpot" @submitSuccess="handleEditSuccess" @cancel="showEditModal = false" />
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&display=swap');

body {
  font-family: your-current-font, 'Noto Color Emoji', sans-serif;
}

/* ☠️ 骨架屏 Skeleton Loading 動畫樣式 */
.skeleton-card { cursor: default; pointer-events: none; }
.skeleton-img { height: 180px; width: 100%; background: var(--border-color); animation: pulse 1.5s infinite ease-in-out; }
.skeleton-title { height: 20px; width: 80%; background: var(--border-color); border-radius: 4px; margin-bottom: 8px; animation: pulse 1.5s infinite ease-in-out; }
.skeleton-title.short { width: 40%; margin-bottom: 15px; }
.skeleton-text { height: 14px; width: 60%; background: var(--border-color); border-radius: 4px; margin-bottom: 10px; animation: pulse 1.5s infinite ease-in-out; }
.skeleton-text.block { width: 100%; height: 16px; margin: 0; }
.skeleton-tags { display: flex; gap: 8px; margin-top: 15px; margin-bottom: auto; }
.skeleton-tag { height: 22px; width: 60px; background: var(--border-color); border-radius: 6px; animation: pulse 1.5s infinite ease-in-out; }
.skeleton-footer { display: flex; align-items: center; }

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 0.2; }
  100% { opacity: 0.6; }
}

/* Toast 提示系統樣式 */
.toast-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: var(--text-color);
  color: var(--bg-color);
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  z-index: 10000;
  font-weight: bold;
  animation: slideUpFade 0.3s ease-out forwards;
}
@keyframes slideUpFade {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.spot-container { --gap: 20px; padding: 20px; max-width: 1300px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 15px; }
.header-left h2 { display: flex; align-items: center; gap: 8px; margin: 0; }

.text-primary { color: var(--primary-color); }
.text-muted { color: var(--text-secondary); }

.grid-layout { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--gap); align-items: start; }
@media (max-width: 1150px) { .grid-layout { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 850px) { .grid-layout { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 550px) { .grid-layout { grid-template-columns: 1fr; } }

.spot-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px var(--shadow-color); transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; display: flex; flex-direction: column; height: 400px; }
.spot-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
.image-box { position: relative; height: 180px; flex-shrink: 0; overflow: hidden; box-sizing: border-box; }

/* 動態漸層色塊與大標題設計 */
.dynamic-color-box {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
  box-sizing: border-box; 
  transition: filter 0.3s ease;
}
.spot-card:hover .dynamic-color-box {
  filter: brightness(1.15);
}
.spot-title-overlay {
  color: white;
  font-size: 1.4rem; 
  font-weight: 900;
  line-height: 1.4;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  z-index: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word; 
  width: 100%;
}
.modal-title-overlay {
  font-size: 2.2rem;
  text-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
}

.img-rating-badge { position: absolute; top: 10px; right: 10px; background: rgba(255, 215, 0, 0.95); color: #856404; font-weight: 800; font-size: 11px; padding: 3px 8px; border-radius: 20px; display: inline-flex; align-items: center; gap: 3px; z-index: 2; }
.category-tag { position: absolute; top: 10px; left: 10px; background: rgba(255,255,255,0.9); color: var(--primary-color); font-size: 10px; font-weight: bold; padding: 3px 10px; border-radius: 20px; z-index: 2;}
.location-tag { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.6); color: white; font-size: 10px; padding: 4px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 3px; z-index: 2;}

.card-body { padding: 18px; display: flex; flex-direction: column; flex-grow: 1; }

/* 鎖定標題高度，完美對齊 */
.title-row { height: 50px; display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 5px; overflow: hidden; }
.spot-name { margin: 0; font-size: 1.15rem; font-weight: 800; color: var(--text-color); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.3; }
.insufficient-badge { font-size: 10px; color: var(--text-secondary); background: var(--input-bg); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border-color); white-space: nowrap; flex-shrink: 0;}

.info-row { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px; display: flex; align-items: center; }
.info-item { display: inline-flex; align-items: center; gap: 4px; }
.dot-separator { margin: 0 8px; color: #ccc; }

.tags-row { display: flex; gap: 6px; margin-bottom: 15px; flex-wrap: wrap; height: 24px; overflow: hidden; }
.feature-tag { background: var(--input-bg); color: var(--primary-color); border: 1px solid var(--border-color); font-size: 10px; padding: 2px 8px; border-radius: 6px; }

/* 鎖定底部高度與 Flexbox 對齊 Emoji */
.footer { 
  margin-top: auto; 
  border-top: 1px solid var(--border-color); 
  padding-top: 12px; 
  height: 60px; 
  box-sizing: border-box;
  display: flex; 
  align-items: center; 
}

.rec-text { 
  font-size: 0.8rem; 
  color: var(--text-secondary); 
  width: 100%; 
  line-height: 1.4; 
  display: -webkit-box; 
  -webkit-line-clamp: 2; 
  -webkit-box-orient: vertical; 
  overflow: hidden; 
  text-overflow: ellipsis; 
}

.label { font-weight: bold; display: inline-flex; align-items: center; gap: 3px; }
.rec-content { color: var(--text-color); }

.btn-action { padding: 6px 14px; border-radius: 6px; border: none; cursor: pointer; font-size: 0.85rem; font-weight: bold; transition: all 0.2s ease; letter-spacing: 1px; display: inline-flex; align-items: center; gap: 4px; }
.btn-action.btn-edit { background-color: var(--input-bg); color: var(--text-secondary); border: 1px solid var(--border-color); }
.btn-action.btn-edit:hover { color: var(--primary-color); border-color: var(--primary-color); background-color: rgba(50, 100, 255, 0.05); }
.btn-action.btn-add { background-color: var(--primary-color); color: white; }
.btn-action.btn-add:hover { opacity: 0.9; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(50, 100, 255, 0.3); }

.btn-primary {
    background-color: var(--primary-color);
    color: #fff;
    border-radius: var(--radius-md);
    padding: 8px 16px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    transition: all .3s ease;
}

.state-box { padding: 40px; text-align: center; color: var(--text-secondary); display: flex; align-items: center; justify-content: center; gap: 8px; }
.retry-btn { display: inline-flex; align-items: center; gap: 4px; margin-left: 10px; padding: 4px 10px; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }

/* 彈窗詳細資訊樣式對齊調整 */
.detail-modal-card { background: var(--card-bg); border-radius: 16px; width: 90%; max-width: 1000px; max-height: 85vh; position: relative; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.3); animation: modalScaleIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes modalScaleIn { from { opacity: 0; transform: scale(0.95) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }
.modal-close-btn { position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.5); color: white; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 1.2rem; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
.modal-close-btn:hover { background: var(--primary-color); }
.detail-layout { display: flex; height: 85vh; }
.detail-info-side { flex: 6; display: flex; flex-direction: column; overflow-y: auto; }
.detail-image-box { width: 100%; height: 300px; position: relative; flex-shrink: 0; }
.detail-img-overlay { position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, rgba(0,0,0,0.8), transparent); display: flex; align-items: flex-end; z-index: 2; }
.detail-category { background: var(--primary-color); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; font-weight: bold; }
.detail-content { padding: 30px; }
.detail-content h2 { margin: 0 0 10px 0; font-size: 2rem; color: var(--text-color); }

.detail-location { color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 25px; display: inline-flex; align-items: center; gap: 6px; }

.detail-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; background: var(--input-bg); padding: 20px; border-radius: 12px; margin-bottom: 30px; border: 1px solid var(--border-color); }
.meta-item { display: flex; align-items: flex-start; gap: 12px; }
.meta-item .icon { font-size: 1.5rem; display: inline-flex; align-items: center; justify-content: center; height: 24px; }
.meta-item .text strong { display: block; font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 4px; }
.meta-item .text span { font-size: 1.05rem; color: var(--text-color); font-weight: bold; }
.detail-tags-section { margin-bottom: 25px; }
.detail-tags-section h4 { margin: 0 0 10px 0; font-size: 1rem; color: var(--text-color); }
.detail-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.detail-tags .tag { background: rgba(50, 100, 255, 0.1); color: var(--primary-color); padding: 6px 12px; border-radius: 8px; font-size: 0.9rem; font-weight: bold; }
.detail-tags .act-tag { background: white; border: 1px solid var(--border-color); color: var(--text-secondary); padding: 6px 12px; border-radius: 8px; font-size: 0.9rem; }
.detail-actions { display: flex; gap: 15px; margin-top: 30px; border-top: 1px solid var(--border-color); padding-top: 25px; }
.detail-actions .btn-action { flex: 1; padding: 12px; font-size: 1rem; justify-content: center; }
.detail-review-side { flex: 4; border-left: 1px solid var(--border-color); background: var(--input-bg); overflow-y: auto; }

@media (max-width: 850px) {
  .detail-layout { flex-direction: column ; }
  .detail-review-side { border-left: none; border-top: 1px solid var(--border-color); min-height: 400px; }
  .detail-image-box { height: 200px; }
}

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 9999; backdrop-filter: blur(2px); }
.modal-content { background: var(--card-bg); padding: 25px; border-radius: 12px; width: 90%; max-width: 400px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
.modal-select { width: 100%; padding: 10px; margin: 20px 0; border-radius: 6px; border: 1px solid var(--border-color); background: var(--input-bg); color: var(--text-color); }
.modal-actions { display: flex; gap: 10px; justify-content: center; }
.btn-confirm { background: #2ecc71; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.btn-cancel { background: #e74c3c; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.modal-inner { width: 95%; max-width: 800px; max-height: 90vh; overflow-y: auto; background: var(--card-bg); border-radius: 16px; }

.hero-section { position: relative; background-image: url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; height: 400px; display: flex; align-items: center; justify-content: center; margin-bottom: 60px; border-radius: 10px; }
.hero-title { color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.5); font-size: 2.5rem; text-align: center; margin-bottom: 20px; }

/* 搜尋卡片對齊優化 */
.search-card { background: var(--card-bg); border-radius: var(--radius-lg); box-shadow: var(--shadow-md); padding: 20px; width: 100%; max-width: 800px; position: absolute; bottom: -40px; left: 50%; transform: translateX(-50%); border: 1px solid var(--border-color); }
.search-tabs { display: flex; gap: 20px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; margin-bottom: 15px; }
.search-tabs span { font-weight: bold; cursor: pointer; color: var(--text-secondary); display: inline-flex; align-items: center; gap: 4px; }
.search-tabs span.active { color: var(--primary-color); border-bottom: 3px solid var(--primary-color); padding-bottom: 11px; }
.search-inputs { display: flex; gap: 10px; }
.search-inputs input { flex: 1; padding: 12px 16px; border: 1px solid var(--border-color); border-radius: var(--radius-md); font-size: 1rem; background: var(--input-bg); color: var(--text-color); outline: none; }
.search-inputs input:focus { border-color: var(--primary-color); }
.search-btn { width: 120px; font-size: 1.1rem; }
</style>
