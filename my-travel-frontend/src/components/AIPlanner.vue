<script setup>
import { ref } from 'vue'
import api from '../api/axios.js' // 引用設定好的 api

// 1. 定義 emit (這樣才能跳轉去登入頁)
const emit = defineEmits(['changePage'])

const props = defineProps({
  isLoggedIn: Boolean
})

// 狀態變數
const form = ref({
  destination: '台北',
  days: 1,
  style: ''
})

// 2. 變數名稱改得更直覺，且與儲存函式統一
const generatedItinerary = ref([]) 
const isLoading = ref(false)
const isSaving = ref(false)

// --- 呼叫 AI 生成行程 ---
const generatePlan = async () => {
  if (!form.value.destination) return alert('請輸入地點！')
  
  isLoading.value = true
  generatedItinerary.value = [] // 清空上次結果
  
  try {
    // 3. 修改這裡：使用 api.post
    // (注意：請確認後端 routers/ai_plan.py 的路徑前綴是否正確，假設是 /api)
    const response = await api.post('/api/generate_itinerary', form.value, {
      timeout: 60000 // 60秒
    })
    
    generatedItinerary.value = response.data.result
  } catch (error) {
    console.error(error)
    alert('AI 發生錯誤，請稍後再試')
  } finally {
    isLoading.value = false
  }
}

// --- 儲存行程到資料庫 ---
const handleSaveToMyTrip = async () => {
  // 1. 檢查登入狀態
  
  if (!props.isLoggedIn) {
    if(confirm('您需要登入才能儲存行程！是否前往登入頁面？')) {
      emit('changePage', 'login') // 跳轉到登入頁
    }
    return
  }

  try {
    isSaving.value = true
    
    // 2. 準備 payload
    const payload = {
      title: `${form.value.destination} ${form.value.days}日遊 (AI推薦)`,
      spots: generatedItinerary.value.map(item => ({
        name: item.name,
        day: item.day,
        description: item.description
      }))
    }

    // 3. 呼叫後端儲存 API
    await api.post('/api/itineraries/from_ai', payload)
    
    alert('🎉 成功加入您的行程表！')
    
  } catch (error) {
    console.error(error)
    alert('❌ 儲存失敗，請稍後再試')
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="ai-container">
    <h2>🤖 AI 智能行程規劃</h2>
    
    <div class="input-group">
      <input v-model="form.destination" placeholder="你想去哪裡？(ex: 高雄)" />
      
      <div class="days-input-wrapper">
        <input 
          type="number" 
          v-model.number="form.days" 
          placeholder="天數"
          min="1" 
          max="30" 
        /> 
        <span class="unit-text">天</span>
      </div>
      
      <input 
        v-model="form.style" 
        placeholder="想怎麼玩？(ex: 文青、省錢)" 
        class="style-input"
      />
      
      <button @click="generatePlan" :disabled="isLoading">
        {{ isLoading ? '規劃中...' : '開始生成 ✨' }}
      </button>
    </div>

    <div v-if="isLoading" class="loading">
      AI 正在絞盡腦汁幫你排行程...🧠
    </div>

    <div v-if="generatedItinerary.length > 0" class="result-section">
      
      <div v-for="spot in generatedItinerary" :key="spot.name" class="ai-card">
        <h4>Day {{ spot.day }} {{ spot.time_of_day }} - {{ spot.name }}</h4>
        <p>{{ spot.description }}</p>
        <small>📍 {{ spot.address }}</small>
      </div>

      <div class="action-buttons">
        <button 
          class="save-btn" 
          @click="handleSaveToMyTrip" 
          :disabled="isSaving"
        >
          {{ isSaving ? '儲存中...' : (isLoggedIn ? '💾 加入我的行程' : '🔐 登入後儲存行程') }}
        </button>
      </div>
    </div>
    
  </div>
</template>

<style scoped>
.ai-container { max-width: 600px; margin: 20px auto; padding: 20px; }
.input-group { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
input, select, button { padding: 10px; border-radius: 5px; border: 1px solid #ddd; }

/* 讓所有輸入框高度一致 */
input, select, button { height: 42px; box-sizing: border-box; }

/* 生成按鈕 */
button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
button:disabled { background-color: #ccc; }

.days-input-wrapper { position: relative; display: flex; align-items: center; }
.days-input-wrapper input { width: 80px; padding-right: 25px; text-align: center; }
.unit-text { position: absolute; right: 15px; color: #888; font-size: 14px; pointer-events: none; }
.style-input { flex: 1; min-width: 150px; }

/* --- 結果卡片樣式 --- */
.ai-card {
  background: #fff;
  border: 1px solid #eee;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  border-left: 5px solid #4CAF50; /* 綠色左邊條 */
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.ai-card h4 { margin: 0 0 5px 0; color: #333; }
.ai-card p { margin: 5px 0; color: #666; font-size: 0.95rem; }
.ai-card small { color: #999; }

.loading { text-align: center; color: #666; font-style: italic; margin-top: 20px; }

/* --- ✨ 儲存按鈕樣式 --- */
.action-buttons { margin-top: 20px; text-align: center; padding-bottom: 20px; }

.save-btn {
  background: linear-gradient(135deg, #FF6B6B, #FF8E53); /* 漂亮的漸層橘紅色 */
  color: white;
  font-size: 1.1rem;
  font-weight: bold;
  padding: 0 30px; /* 高度已由上面統一定義，這裡定寬度 */
  border-radius: 25px;
  box-shadow: 0 4px 10px rgba(255, 107, 107, 0.3);
  transition: transform 0.2s;
}
.save-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(255, 107, 107, 0.4); }
</style>