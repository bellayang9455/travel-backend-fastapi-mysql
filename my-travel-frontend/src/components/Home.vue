<script setup>
// 首頁景點列表 (完美比例版：使用雙重網格鎖定，解決位移與高度不一問題)
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

const fetchSpots = async (keyword = '') => {
  loading.value = true
  try {
    const response = await api.get(`/api/spots`, { params: { q: keyword } })
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

onMounted(() => {
  fetchSpots(route.query.q || '')
  if (props.user) fetchUserItineraries()
})

watch(() => route.query.q, (newK) => fetchSpots(newK || ''))
watch(() => props.user, (newUser) => {
    if (newUser) fetchUserItineraries();
    else itineraries.value = [];
});

const openEditModal = (spot) => {
  currentEditSpot.value = spot
  showEditModal.value = true
}

const handleEditSuccess = () => {
  showEditModal.value = false
  fetchSpots()
}
</script>

<template>
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

    <!-- 外部網格：固定比例與對齊 -->
    <div v-else class="grid-layout">
      <div 
        v-for="spot in sortedSpots" 
        :key="spot.id" 
        class="card-wrapper"
        :class="{ 'is-expanded': expandedSpotId === spot.id }"
        @click="toggleExpand(spot.id)"
      >
        <div class="expandable-card">
          
          <!-- 左側資訊側：固定寬度、比例與位置 -->
          <div class="card-info-side">
            <div class="image-box">
              <img :src="getImageUrl(spot.id)" alt="景點圖片">
              <span class="category-tag">{{ spot.category || '未分類' }}</span>
              <span class="location-tag" v-if="spot.location">📍 {{ spot.location }}</span>
            </div>

            <div class="card-body">
              <h3 class="spot-name">{{ spot.name }}</h3>
              <div class="info-row"><span>🕒 {{ spot.hours || '全天開放' }}</span></div>
              <div class="tags-row">
                <template v-if="spot.features?.features?.length > 0 && spot.features.features[0] !== ''">
                  <span v-for="(tag, index) in spot.features.features.slice(0, 3)" :key="index" class="feature-tag">#{{ tag }}</span>
                </template>
              </div>
              <div class="footer">
                 <div class="rec-text">
                     <span class="label">推薦：</span>
                     <span>{{ spot.activities?.activities?.slice(0, 2).join('、') || '自由探索' }}</span>
                 </div>
                 <div class="actions" @click.stop>
                    <button @click="openEditModal(spot)" class="btn-circle warn" title="編輯">✏️</button>
                    <button @click="openAddModal(spot.id)" class="btn-circle primary" title="加入行程">📅</button>
                 </div>
              </div>
            </div>
          </div>

          <!-- 👉 右側評論側：展開後平滑長出 -->
          <div v-if="expandedSpotId === spot.id" class="card-review-side" @click.stop>
            <ReviewSection :spotId="spot.id" :user="props.user" />
          </div>

        </div>
      </div>
    </div>

    <!-- Modals -->
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
</template>

<style scoped>
.spot-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 15px; }

/* 🏛️ 外部網格佈局：確保一排固定四個，且對齊頂部 */
.grid-layout {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  align-items: start; /* ✨ 關鍵：防止同列卡片被強行拉長 */
}

@media (max-width: 1100px) { .grid-layout { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 850px) { .grid-layout { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .grid-layout { grid-template-columns: 1fr; } }

.card-wrapper {
  transition: all 0.3s ease;
  cursor: pointer;
}

.card-wrapper.is-expanded {
  grid-column: span 2; /* 展開時跨越兩欄 */
}

/* 📦 卡片容器：內部也使用 Grid 佈局以確保完美對齊 */
.expandable-card {
  display: grid;
  grid-template-columns: 1fr; /* 預設一欄 */
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 8px var(--shadow-color);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  height: 400px; /* ✨ 固定高度，解決比例不一問題 */
}

.is-expanded .expandable-card {
  grid-template-columns: 1fr 1fr; /* 展開變兩欄 */
  column-gap: 20px; /* ✨ 必須與外部網格 Gap 相同，才能防止位移 */
}

/* 👈 左側資訊側 */
.card-info-side {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0; /* 防止內容撐開 */
}

/* 👉 右側評論側 */
.card-review-side {
  border-left: 1px solid var(--border-color);
  background: var(--input-bg);
  display: flex;
  flex-direction: column;
  height: 100%;
  animation: slideIn 0.5s ease-out forwards;
  overflow: hidden;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* 內部細節：恢復原始比例 */
.image-box { position: relative; height: 160px; flex-shrink: 0; overflow: hidden; }
.image-box img { width: 100%; height: 100%; object-fit: cover; }

.category-tag { position: absolute; top: 10px; left: 10px; background: rgba(255,255,255,0.9); color: var(--primary-color); font-size: 11px; font-weight: bold; padding: 3px 10px; border-radius: 20px; }
.location-tag { position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.6); color: white; font-size: 11px; padding: 3px 8px; border-radius: 4px; }

.card-body { padding: 15px; display: flex; flex-direction: column; flex-grow: 1; min-height: 0; }
.spot-name { margin: 0 0 8px 0; font-size: 1.05rem; font-weight: bold; color: var(--text-color); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.info-row { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 10px; }
.tags-row { display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; height: 24px; overflow: hidden; }
.feature-tag { background: var(--input-bg); color: var(--primary-color); border: 1px solid var(--border-color); font-size: 10px; padding: 2px 8px; border-radius: 4px; }

.footer { margin-top: auto; border-top: 1px solid var(--border-color); padding-top: 12px; display: flex; justify-content: space-between; align-items: center; }
.rec-text { font-size: 0.8rem; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.label { font-weight: bold; color: var(--text-color); }

.actions { display: flex; gap: 8px; }
.btn-circle { width: 30px; height: 30px; border-radius: 50%; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; transition: transform 0.2s; }
.btn-circle.primary { background: var(--primary-color); color: white; }
.btn-circle.warn { background: #f39c12; color: white; }

/* RWD 調整 */
@media (max-width: 600px) { 
  .card-wrapper.is-expanded { grid-column: span 1; }
  .expandable-card, .is-expanded .expandable-card { grid-template-columns: 1fr; height: auto; min-height: 400px; }
  .card-review-side { border-left: none; border-top: 1px solid var(--border-color); }
}

.modal-inner { width: 95%; max-width: 800px; max-height: 90vh; overflow-y: auto; }
</style>