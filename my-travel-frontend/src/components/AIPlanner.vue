<script setup>
// AI 行程規劃元件
import { ref } from 'vue'
import api from '../api/axios.js'

const emit = defineEmits(['changePage'])

const props = defineProps({
  isLoggedIn: Boolean,
  user: Object
})

const form = ref({
  destination: '台北',
  days: 1,
  style: ''
})

const generatedItinerary = ref([]) 
const isLoading = ref(false)
const isSaving = ref(false)

// 呼叫 AI 生成行程
const generatePlan = async () => {
  if (!form.value.destination) return alert('請輸入地點！')
  
  isLoading.value = true
  generatedItinerary.value = [] 
  
  try {
    // 💡 確保這裡的路徑是加上 /ai-plan 的正確版本
    const response = await api.post('/api/ai-plan/generate_itinerary', form.value, {
      timeout: 60000 
    })
    
    generatedItinerary.value = response.data.result
  } catch (error) {
    console.error(error)
    alert('AI 發生錯誤，請稍後再試')
  } finally {
    isLoading.value = false
  }
}

// 儲存行程到資料庫
const handleSaveToMyTrip = async () => {
  if (!props.isLoggedIn || !props.user) {
    if(confirm('您需要登入才能儲存行程！是否前往登入頁面？')) {
      emit('changePage', 'login')
    }
    return
  }

  try {
    isSaving.value = true
    
    const payload = {
      title: `${form.value.destination} ${form.value.days}日遊 (AI推薦)`,
      user_id: props.user.id,
      spots: generatedItinerary.value.map(item => ({
        name: item.name,
        day: item.day,
        description: item.description
      }))
    }

    await api.post('/api/itineraries/from_ai', payload)
    alert('🎉 成功加入您的行程表！')
    
  } catch (error) {
    console.error('❌ 儲存失敗，請稍後再試', error)

    if (error.response && error.response.status === 401) {
        alert("⚠️ 您的登入憑證已失效，請重新登入。")
        emit('changePage', 'login')
    } else {
        const errorMsg = error.response?.data?.detail || "未知錯誤";
        alert(`❌ 儲存失敗：${errorMsg}`);
    }
  } finally {
    isSaving.value = false
  }
}

const getTransportIcon = (text) => {
  if (!text) return '🚗'; 
  
  if (text.includes('步') || text.includes('走')) return '🚶';
  else if (text.includes('捷運') || text.includes('地鐵') || text.includes('鐵')) return '🚇';
  else if (text.includes('公車') || text.includes('巴士')) return '🚌';
  else if (text.includes('計程車') || text.includes('Uber') || text.includes('租車')) return '🚕';
  else if (text.includes('自行前往')) return '📍';
  
  return '🚗'; 
}
</script>

<script>
export default { name: 'AIPlanner' }
</script>

<template>
  <div class="ai-container">
    
    <div class="planner-header">
      <h2>🤖 AI 智能行程規劃</h2>
      <p class="subtitle">輸入您的目的地與偏好，讓 AI 為您打造完美專屬旅程</p>
    </div>
    
    <div class="search-panel">
      <div class="input-grid">
        <div class="input-item destination">
          <label>目的地</label>
          <input v-model="form.destination" placeholder="你想去哪裡？ (ex: 大阪、高雄)" />
        </div>
        
        <div class="input-item days">
          <label>旅遊天數</label>
          <div class="days-input-wrapper">
            <input type="number" v-model.number="form.days" min="1" max="30" /> 
            <span class="unit-text">天</span>
          </div>
        </div>
        
        <div class="input-item style">
          <label>旅行風格</label>
          <input v-model="form.style" placeholder="想怎麼玩？ (ex: 文青、省錢、親子)" />
        </div>
      </div>
      
      <button class="btn-generate" @click="generatePlan" :disabled="isLoading">
        {{ isLoading ? 'AI 正在為您規劃中...' : '✨ 立即生成專屬行程' }}
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="loader"></div>
      <p>正在分析上萬筆旅遊數據，為您規劃最棒的路線... 🧠</p>
    </div>

    <div v-if="generatedItinerary.length > 0 && !isLoading" class="result-section">
      <h3 class="result-title">為您規劃的 {{ form.destination }} {{ form.days }}日遊</h3>
      
      <div class="timeline">
        <div v-for="(spot, index) in generatedItinerary" :key="spot.name" class="timeline-item">
          
          <div v-if="index === 0 || spot.day !== generatedItinerary[index - 1].day" class="day-divider">
            <span class="day-badge">Day {{ spot.day }}</span>
          </div>

          <div v-if="index > 0 && spot.transportation && spot.day === generatedItinerary[index - 1].day" class="transport-box">
            <div class="trans-line"></div>
            <div class="trans-tag">
               {{ getTransportIcon(spot.transportation) }} {{ spot.transportation }}
            </div>
          </div>
          <div v-else-if="index > 0 && spot.day === generatedItinerary[index - 1].day" class="transport-box">
             <div class="trans-line-only"></div>
          </div>

          <div class="ai-spot-card">
            <div class="time-indicator">{{ spot.time_of_day || '全天' }}</div>
            <div class="card-content">
              <h4>{{ spot.name }}</h4>
              <p class="desc">{{ spot.description }}</p>
              <div class="card-footer">
                <span class="location">📍 {{ spot.address || spot.location || '暫無詳細地址' }}</span>
                <span v-if="spot.category" class="category-tag">{{ spot.category }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <div class="action-buttons">
        <button class="btn-save-trip" @click="handleSaveToMyTrip" :disabled="isSaving">
          {{ isSaving ? '儲存中...' : (isLoggedIn ? '💾 一鍵加入我的行程' : '🔐 登入以儲存此行程') }}
        </button>
      </div>
    </div>
    
  </div>
</template>

<style scoped>
.ai-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  color: var(--text-color);
}

.planner-header {
  text-align: center;
  margin-bottom: 30px;
}

.planner-header h2 {
  font-size: 2.2rem;
  color: var(--text-color);
  margin: 0 0 10px 0;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin: 0;
}

/* 搜尋面板卡片 */
.search-panel {
  background: var(--card-bg);
  padding: 30px;
  border-radius: 16px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  margin-bottom: 40px;
}

.input-grid {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
}

.input-item {
  display: flex;
  flex-direction: column;
}

.input-item label {
  font-size: 0.9rem;
  font-weight: bold;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.input-item.destination { flex: 2; }
.input-item.days { flex: 1; min-width: 100px; }
.input-item.style { flex: 2; }

input {
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--input-bg);
  color: var(--text-color);
  font-size: 1rem;
  transition: all 0.3s;
}

input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(50, 100, 255, 0.1);
}

.days-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.days-input-wrapper input {
  width: 100%;
  padding-right: 40px;
}

.unit-text {
  position: absolute;
  right: 15px;
  color: var(--text-secondary);
  font-weight: bold;
  pointer-events: none;
}

.btn-generate {
  width: 100%;
  padding: 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(50, 100, 255, 0.3);
}

.btn-generate:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(50, 100, 255, 0.4);
}

.btn-generate:disabled {
  background: #ccc;
  box-shadow: none;
  cursor: not-allowed;
}

/* 載入動畫 */
.loading-state {
  text-align: center;
  padding: 50px 0;
  color: var(--primary-color);
  font-weight: bold;
}

.loader {
  border: 4px solid rgba(50, 100, 255, 0.1);
  border-left-color: var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px auto;
}

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* 結果時間軸區域 */
.result-section {
  animation: fadeIn 0.5s ease-out;
}

.result-title {
  text-align: center;
  font-size: 1.6rem;
  color: var(--text-color);
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px dashed var(--border-color);
}

.timeline {
  display: flex;
  flex-direction: column;
  padding: 0 10px;
}

.timeline-item {
  position: relative;
  display: flex;
  flex-direction: column;
}

/* 天數分隔線 */
.day-divider {
  display: flex;
  justify-content: center;
  margin: 30px 0 15px 0;
  position: relative;
}

.day-divider::before {
  content: '';
  position: absolute;
  top: 50%; left: 0; right: 0;
  height: 1px;
  background: var(--border-color);
  z-index: 1;
}

.day-badge {
  background: var(--text-color);
  color: white;
  padding: 6px 24px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 1.1rem;
  z-index: 2;
  box-shadow: var(--shadow-sm);
}

/* 交通線 */
.transport-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 5px 0;
}

.trans-line {
  width: 2px;
  height: 20px;
  background: var(--border-color);
}

.trans-line-only {
  width: 2px;
  height: 30px;
  background: var(--border-color);
}

.trans-tag {
  background: var(--input-bg);
  color: var(--text-secondary);
  font-size: 0.85rem;
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

/* 景點卡片 */
.ai-spot-card {
  display: flex;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.ai-spot-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
}

.time-indicator {
  background: rgba(50, 100, 255, 0.05);
  color: var(--primary-color);
  width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
  border-right: 1px solid var(--border-color);
}

.card-content {
  padding: 20px;
  flex: 1;
}

.card-content h4 {
  margin: 0 0 10px 0;
  font-size: 1.25rem;
  color: var(--text-color);
}

.desc {
  margin: 0 0 15px 0;
  color: var(--text-secondary);
  line-height: 1.5;
  font-size: 0.95rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  padding-top: 15px;
  border-top: 1px dashed var(--border-color);
}

.location {
  color: var(--text-secondary);
  font-weight: 500;
}

.category-tag {
  background: var(--primary-color);
  color: white;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

/* 儲存按鈕 */
.action-buttons {
  margin-top: 40px;
  text-align: center;
  padding-bottom: 20px;
}

.btn-save-trip {
  background: var(--text-color);
  color: white;
  font-size: 1.2rem;
  font-weight: bold;
  padding: 16px 40px;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  box-shadow: 0 6px 15px rgba(0,0,0,0.15);
  transition: all 0.2s;
}

.btn-save-trip:hover:not(:disabled) {
  transform: translateY(-3px);
  background: var(--primary-color);
  box-shadow: 0 8px 20px rgba(50, 100, 255, 0.4);
}

.btn-save-trip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* RWD 響應式 */
@media (max-width: 768px) {
  .input-grid { flex-direction: column; gap: 15px; }
  .ai-spot-card { flex-direction: column; }
  .time-indicator { width: 100%; padding: 10px; border-right: none; border-bottom: 1px solid var(--border-color); }
  .card-footer { flex-direction: column; align-items: flex-start; gap: 10px; }
}
</style>