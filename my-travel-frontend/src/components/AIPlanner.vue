<script setup>
import { ref } from 'vue';
import axios from 'axios';

// 接收 User.vue 傳來的使用者資訊 (為了拿到 user.id)
const props = defineProps({
    user: Object
});

const emit = defineEmits(['close', 'refresh']);

// --- 表單變數 ---
const destination = ref('台北'); // 預設值
const days = ref(3);
const budget = ref(5000);
const style = ref('在地美食');

// --- 狀態控制 ---
const loading = ref(false); // 控制是否正在生成中
const API_URL = "http://localhost:8000";

// --- 呼叫 AI API ---
const generatePlan = async () => {
    // 1. 基本檢查
    if (!props.user) {
        alert("請先登入才能使用 AI 功能喔！");
        return;
    }

    loading.value = true; // 開始轉圈圈

    try {
        // 2. 準備傳給後端的資料 (對應後端 AIPlanRequest 格式)
        const payload = {
            destination: destination.value,
            days: parseInt(days.value),
            budget: parseInt(budget.value),
            style: style.value,
            owner_id: props.user.id
        };

        // 3. 發送請求
        const res = await axios.post(`${API_URL}/ai/generate_itinerary`, payload);
        
        // 4. 成功處理
        alert("✨ " + res.data.message);
        emit('refresh'); // 通知父元件 (User.vue) 重新抓取行程列表
        emit('close');   // 關閉視窗

    } catch (e) {
        console.error(e);
        // 顯示錯誤訊息
        if (e.response && e.response.data) {
             alert("出錯了：" + e.response.data.detail);
        } else {
             alert("AI 目前忙碌中，請稍後再試 😭");
        }
    } finally {
        loading.value = false; // 停止轉圈圈
    }
};
</script>

<template>
  <div class="modal-overlay">
    <div class="modal-content ai-card">
      
      <div class="ai-header">
        <h3>🤖 AI 智慧行程規劃</h3>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>
      
      <div class="form-body">
          <div class="form-group">
            <label>📍 你想去哪裡？</label>
            <input v-model="destination" placeholder="例如：台南、京都、巴黎" />
          </div>

          <div class="form-group">
            <label>📅 去幾天？ ({{ days }} 天)</label>
            <input type="range" v-model="days" min="1" max="10" />
            <div class="range-labels">
                <span>1天</span>
                <span>10天</span>
            </div>
          </div>

          <div class="form-group">
            <label>💰 預算 (台幣) ${{ budget }}</label>
            <input type="number" v-model="budget" step="1000" />
          </div>

          <div class="form-group">
            <label>🎨 喜歡什麼風格？</label>
            <select v-model="style">
                <option value="在地美食">🍜 在地美食吃飽飽</option>
                <option value="網美打卡">📸 網美景點拍美照</option>
                <option value="歷史文化">🏯 歷史古蹟深度遊</option>
                <option value="自然放鬆">🌲 大自然放鬆之旅</option>
                <option value="極限冒險">🧗 極限運動冒險</option>
                <option value="購物血拼">🛍️ 購物商圈買買買</option>
            </select>
          </div>

          <button @click="generatePlan" class="btn-magic" :disabled="loading">
              <span v-if="loading">🔮 AI 正在通靈中...請稍候</span>
              <span v-else>✨ 開始生成行程</span>
          </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* 遮罩層 */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 2000;
  backdrop-filter: blur(3px); /* 背景模糊特效 */
}

/* 卡片本體 */
.ai-card {
  background: #ffffff;
  padding: 30px; border-radius: 20px; width: 90%; max-width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
  border: 1px solid rgba(255,255,255,0.5);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

/* 標題區 */
.ai-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.ai-header h3 { 
    margin: 0; font-size: 1.5rem;
    background: linear-gradient(45deg, #6a11cb, #2575fc); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    font-weight: 800; 
}
.close-btn { background: none; border: none; font-size: 2rem; cursor: pointer; color: #999; line-height: 1; }
.close-btn:hover { color: #333; }

/* 表單樣式 */
.form-group { margin-bottom: 20px; }
.form-body label { display: block; margin-bottom: 8px; font-weight: bold; color: #444; font-size: 0.95rem; }

input[type="text"], input[type="number"], select { 
    width: 100%; padding: 12px; border-radius: 10px; border: 2px solid #eee; 
    box-sizing: border-box; font-size: 1rem; transition: border-color 0.3s;
}
input:focus, select:focus { outline: none; border-color: #2575fc; }

/* 滑桿樣式 */
input[type=range] { width: 100%; cursor: pointer; }
.range-labels { display: flex; justify-content: space-between; font-size: 0.8rem; color: #888; margin-top: 5px;}

/* 魔法按鈕 */
.btn-magic {
  margin-top: 10px; width: 100%; padding: 15px; border: none; border-radius: 50px;
  background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
  color: white; font-weight: bold; font-size: 1.1rem; cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 10px 20px rgba(37, 117, 252, 0.3);
}
.btn-magic:hover { transform: translateY(-2px); box-shadow: 0 15px 25px rgba(37, 117, 252, 0.5); }
.btn-magic:disabled { background: #ccc; cursor: not-allowed; transform: none; box-shadow: none; }
</style>