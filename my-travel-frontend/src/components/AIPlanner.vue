<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 狀態變數
const form = ref({
  destination: '台北',
  days: 1,
  style: ''
})

const result = ref('')
const isLoading = ref(false)

// 呼叫後端 API
const generatePlan = async () => {
  if (!form.value.destination) return alert('請輸入地點！')
  
  isLoading.value = true
  result.value = '' // 清空上次結果
  
  try {
    // 假設你的後端在 localhost:8000
    const response = await axios.post('http://localhost:8000/api/generate_itinerary', form.value)
    result.value = response.data.result
  } catch (error) {
    console.error(error)
    alert('AI 發生錯誤，請稍後再試')
  } finally {
    isLoading.value = false
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
          style="width: 70px;" 
        /> 
        <span class="unit-text">天</span>
      </div>
      
      <input 
        v-model="form.style" 
        placeholder="想怎麼玩？(ex: 文青、省錢、動漫)" 
        class="style-input"
      />
      
      <button @click="generatePlan" :disabled="isLoading">
        {{ isLoading ? '規劃中...' : '開始生成 ✨' }}
      </button>
    </div>

    <div v-for="spot in result" :key="spot.name" class="ai-card">
      <h4>Day {{ spot.day }} {{ spot.time_of_day }} - {{ spot.name }}</h4>
      <p>{{ spot.description }}</p>
      <small>📍 {{ spot.address }}</small>
    </div>
    
    <div v-if="isLoading" class="loading">
      AI 正在絞盡腦汁幫你排行程...🧠
    </div>
  </div>
</template>

<style scoped>
.ai-container { max-width: 600px; margin: 20px auto; padding: 20px; }
.input-group { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
input, select, button { padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
button:disabled { background-color: #ccc; }
.result-box { background: #f9f9f9; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50; }
.markdown-content { white-space: pre-wrap; line-height: 1.6; }
.loading { text-align: center; color: #666; font-style: italic; margin-top: 20px;}
.days-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.days-input-wrapper input {
  width: 80px; /* 寬度不用太寬 */
  padding-right: 25px; /* 留位置給「天」這個字 */
}

.unit-text {
  position: absolute;
  right: 15px; /* 靠右對齊 */
  color: #888;
  font-size: 14px;
  pointer-events: none; /* 讓滑鼠點擊穿透 */
}

/* 讓所有輸入框高度一致，排版比較整齊 */
input, select, button { 
  height: 42px; 
  box-sizing: border-box;
}
</style>