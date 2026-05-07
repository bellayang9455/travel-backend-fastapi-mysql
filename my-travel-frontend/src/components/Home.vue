<script setup>
// 首頁景點列表 (修正版：推薦文字支援換行)
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router';
import api from '../api/axios.js'
import SpotForm from './SpotForm.vue'
import ReviewSection from '../components/ReviewSection.vue'; 

const props = defineProps({
  user: Object,
  initialCategory: String
})
const route = useRoute();
const router = useRouter();

// 狀態變數
const spots = ref([])
const itineraries = ref([])
const loading = ref(true)
const errorMessage = ref('')
const sortBy = ref('newest')
const selectedCategory = ref(props.initialCategory || '全部')

// ✨ 展開控制邏輯
const expandedSpotId = ref(null);
const toggleExpand = (id) => {
  expandedSpotId.value = expandedSpotId.value === id ? null : id;
};

// 彈出視窗
const showAddModal = ref(false)
const selectedSpotId = ref(null)
const selectedItineraryId = ref('')
const showEditModal = ref(false)
const currentEditSpot = ref(null)

const getImageUrl = (id) => `https://picsum.photos/seed/${id}/400/300`

const sortedSpots = computed(() => {
  let list = [...spots.value]
  if (selectedCategory.value !== '全部') {
    list = list.filter(spot => (spot.category || '未分類').includes(selectedCategory.value))
  }
  if (route.query.location) {
    list = list.filter(spot => spot.region === route.query.location)
  }
  
  if (sortBy.value === 'newest') return list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  if (sortBy.value === 'oldest') return list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  if (sortBy.value === 'name_asc') return list.sort((a, b) => a.name.localeCompare(b.name, 'zh-Hant'))
  return list
})

// 強化抓取邏輯
const fetchSpots = async (keyword) => {
  const searchK = (typeof keyword === 'string') ? keyword : (route.query.q || '');
  loading.value = true
  try {
    const response = await api.get(`/api/spots`, { params: { q: searchK } })
    spots.value = response.data
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

const openAddModal = (spotId) => {
    if (!props.user) return alert("請先登入！");
    selectedSpotId.value = spotId;
    if (itineraries.value.length > 0) selectedItineraryId.value = itineraries.value[0].id;
    showAddModal.value = true;
};

const addToItinerary = async () => {
    try {
        await api.post(`/api/itineraries/${selectedItineraryId.value}/add_spot`, { spot_id: selectedSpotId.value });
        alert("🎉 成功加入行程！");
        showAddModal.value = false;
    } catch (e) { alert("加入失敗"); }
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
  if (props.user) fetchUserItineraries()
})

watch(() => route.query.q, (newK) => fetchSpots(newK || ''))
watch(() => props.user, (newUser) => {
    if (newUser) fetchUserItineraries();
    else itineraries.value = [];
});
</script>

<template>
<div class="home-page">
  <div class="hero-section">
    <div class="hero-content">
      <h1 class="hero-title">探索你的下一趟完美旅程</h1>
        
      <div class="search-card">
          <div class="search-tabs">
            <span class="active">🏖️ 找景點</span>
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
        <h2>🏝️ 熱門景點列表</h2>
        <span class="category-badge" v-if="selectedCategory !== '全部'">{{ selectedCategory }}</span>
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
      <div 
        v-for="spot in sortedSpots" 
        :key="spot.id" 
        class="card-wrapper"
        :class="{ 'is-expanded': expandedSpotId === spot.id }"
        @click="toggleExpand(spot.id)"
      >
        <div class="expandable-card">
          
          <!-- 👈 左側資訊側 -->
          <div class="card-info-side">
            <div class="image-box">
              <img :src="getImageUrl(spot.id)" alt="景點圖片">
              <span class="category-tag">{{ spot.category || '未分類' }}</span>
              <span class="location-tag" v-if="spot.location">📍 {{ spot.location }}</span>
              
              <div v-if="(spot.review_count || 0) >= 3" class="img-rating-badge">
                 ★ {{ spot.avg_rating }}
              </div>
            </div>

            <div class="card-body">
              <div class="title-row">
                <h3 class="spot-name">{{ spot.name }}</h3>
                <div v-if="(spot.review_count || 0) < 3" class="insufficient-badge">人數不足</div>
              </div>

              <div class="info-row">
                <span class="info-item">🕒 {{ spot.hours || '全天開放' }}</span>
                <span class="dot-separator">•</span>
                <span class="info-item">💬 {{ spot.review_count || 0 }} 則評論</span>
              </div>

              <div class="tags-row">
                <template v-if="spot.features?.features?.length > 0 && spot.features.features[0] !== ''">
                  <span v-for="(tag, index) in spot.features.features.slice(0, 3)" :key="index" class="feature-tag">#{{ tag }}</span>
                </template>
              </div>

              <div class="footer">
                 <!-- ✨ 修正後的推薦文字區塊 -->
                 <div class="rec-text">
                     <span class="label">推薦：</span>
                     <span class="rec-content">{{ spot.activities?.activities?.slice(0, 3).join('、') || '自由探索' }}</span>
                 </div>
                 <div class="actions">
                    <button @click.stop="openEditModal(spot)" class="btn-circle warn" title="編輯">✏️</button>
                    <button @click.stop="openAddModal(spot.id)" class="btn-circle primary" title="加入行程">📅</button>
                 </div>
              </div>
            </div>
          </div>

          <!-- 👉 右側評論側 -->
          <div v-if="expandedSpotId === spot.id" class="card-review-side" @click.stop>
            <ReviewSection 
              :spotId="spot.id" 
              :user="props.user" 
              @submitSuccess="fetchSpots"
            />
          </div>

        </div>
      </div>
    </div>

    <!-- Modals 區域 -->
    <div v-if="showAddModal" class="modal-overlay">
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

    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-inner">
         <SpotForm :spotToEdit="currentEditSpot" @submitSuccess="handleEditSuccess" @cancel="showEditModal = false" />
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.spot-container { 
  --gap: 20px;
  padding: 20px; 
  max-width: 1300px; 
  margin: 0 auto; 
}

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 15px; }

.grid-layout {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--gap);
  align-items: start;
}

@media (max-width: 1150px) { .grid-layout { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 850px) { .grid-layout { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 550px) { .grid-layout { grid-template-columns: 1fr; } }

.card-wrapper {
  transition: all 0.3s ease;
  cursor: pointer;
  width: 100%;
}

.card-wrapper.is-expanded {
  grid-column: span 2;
}

.expandable-card {
  display: flex;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px var(--shadow-color);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  height: 420px; 
  width: 100%;
}

.is-expanded .expandable-card {
  box-shadow: 0 12px 30px var(--shadow-color);
}

.card-info-side {
  flex: 0 0 100%;
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: flex-basis 0.4s ease;
  min-width: 0;
}

.is-expanded .card-info-side {
  flex: 0 0 calc(50% - (var(--gap) / 2));
}

.card-review-side {
  flex: 0 0 calc(50% + (var(--gap) / 2));
  border-left: 1px solid var(--border-color);
  background: var(--input-bg);
  height: 100%;
  animation: slideIn 0.5s ease-out forwards;
  overflow: hidden;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.image-box { position: relative; height: 170px; flex-shrink: 0; overflow: hidden; }
.image-box img { width: 100%; height: 100%; object-fit: cover; }

.img-rating-badge {
  position: absolute; top: 10px; right: 10px; background: rgba(255, 215, 0, 0.95);
  color: #856404; font-weight: 800; font-size: 11px; padding: 3px 8px; border-radius: 20px;
}

.category-tag { position: absolute; top: 10px; left: 10px; background: rgba(255,255,255,0.9); color: var(--primary-color); font-size: 10px; font-weight: bold; padding: 3px 10px; border-radius: 20px; }
.location-tag { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.6); color: white; font-size: 10px; padding: 4px 8px; border-radius: 4px; }

.card-body { padding: 18px; display: flex; flex-direction: column; flex-grow: 1; min-height: 0; }
.title-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 5px; }
.spot-name { margin: 0; font-size: 1.15rem; font-weight: 800; color: var(--text-color); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.3; }
.insufficient-badge { font-size: 10px; color: var(--text-secondary); background: var(--input-bg); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border-color); white-space: nowrap; }

.info-row { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px; display: flex; align-items: center; }
.dot-separator { margin: 0 8px; color: #ccc; }

.tags-row { display: flex; gap: 6px; margin-bottom: 15px; flex-wrap: wrap; height: 24px; overflow: hidden; }
.feature-tag { background: var(--input-bg); color: var(--primary-color); border: 1px solid var(--border-color); font-size: 10px; padding: 2px 8px; border-radius: 6px; }

/* 底部按鈕區 */
.footer { 
  margin-top: auto; 
  border-top: 1px solid var(--border-color); 
  padding-top: 15px; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; /* 改為居中對齊，讓按鈕跟換行後的文字視覺上比較平衡 */
}

/* 推薦文字區塊 */
.rec-text { 
  font-size: 0.8rem; 
  color: var(--text-secondary); 
  flex: 1; 
  margin-right: 10px;
  line-height: 1.4;
  /* 允許換行，並設定最多顯示兩行 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
.label { font-weight: bold; }
.rec-content { color: var(--text-color); }

.actions { display: flex; gap: 8px; flex-shrink: 0; }
.btn-circle { width: 32px; height: 32px; border-radius: 50%; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1rem; transition: transform 0.2s; }
.btn-circle:hover { transform: scale(1.15); }
.btn-circle.primary { background: var(--primary-color); color: white; }
.btn-circle.warn { background: #f39c12; color: white; }

@media (max-width: 600px) { 
  .card-wrapper.is-expanded { grid-column: span 1; }
  .expandable-card { flex-direction: column; height: auto; min-height: 420px; }
  .is-expanded .card-info-side { flex: 0 0 100%; }
  .card-review-side { border-left: none; border-top: 1px solid var(--border-color); flex: 0 0 auto; }
}

.modal-inner { width: 95%; max-width: 800px; max-height: 90vh; overflow-y: auto; background: var(--card-bg); border-radius: 16px; }

.hero-section {
  position: relative;
  background-image: url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=2000&auto=format&fit=crop'); /* 替換成你的旅遊大圖 */
  background-size: cover;
  background-position: center;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 60px; /* 留空間給浮動的搜尋卡片 */
  border-radius: 10px;
}

.hero-title {
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 20px;
}

.search-card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 20px;
  width: 100%;
  max-width: 800px;
  position: absolute;
  bottom: -40px; /* 讓卡片往下凸出一半 */
  left: 50%;
  transform: translateX(-50%);
}

.search-tabs {
  display: flex;
  gap: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.search-tabs span {
  font-weight: bold;
  cursor: pointer;
  color: var(--text-secondary);
}

.search-tabs span.active {
  color: var(--primary-color);
  border-bottom: 3px solid var(--primary-color);
  padding-bottom: 11px; /* 微調對齊底線 */
}

.search-inputs {
  display: flex;
  gap: 10px;
}

.search-inputs input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 1rem;
}

.search-btn {
  width: 120px;
  font-size: 1.1rem;
}
</style>