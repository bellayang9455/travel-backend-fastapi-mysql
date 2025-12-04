<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 定義表單資料 (對應資料庫的新欄位)
const formData = ref({
  name: '',
  category: '',
  location: '',
  hours: '',
  featuresStr: '',   // 用來讓使用者輸入字串，送出時再轉成 JSON
  activitiesStr: ''  // 同上
})

const submitData = async () => {
  try {
    // 1. 資料轉換：把使用者輸入的 "老街, 小吃" 轉成 JSON 格式
    // split(/[,，]/) 支援全形和半形逗號
    const featuresJson = {
      features: formData.value.featuresStr.split(/[,，]/).map(s => s.trim()).filter(s => s)
    }
    
    const activitiesJson = {
      activities: formData.value.activitiesStr.split(/[,，]/).map(s => s.trim()).filter(s => s)
    }

    // 2. 準備要送給後端的最終資料包
    const payload = {
      name: formData.value.name,
      category: formData.value.category,
      location: formData.value.location,
      hours: formData.value.hours,
      features: featuresJson,     // 對應資料庫的 features 欄位
      activities: activitiesJson  // 對應資料庫的 activities 欄位
    }

    // 3. 發送 POST 請求
    // ⚠️ 注意：如果後端有改 API 路徑，這裡可能要確認一下 (例如 /spots)
    await axios.post('http://127.0.0.1:8000/spots', payload)
    
    alert('🎉 新增成功！')
    
    // 4. 清空表單
    formData.value = {
      name: '', category: '', location: '', hours: '', featuresStr: '', activitiesStr: ''
    }
    
  } catch (error) {
    alert('❌ 新增失敗，請檢查後端 Console 或 Network')
    console.error(error)
  }
}
</script>

<template>
  <div class="form-box">
    <h3>➕ 新增私房景點</h3>
    
    <div class="input-group">
      <label>景點名稱</label>
      <input v-model="formData.name" placeholder="例如：九份老街" />
    </div>

    <div class="input-group">
      <label>分類</label>
      <select v-model="formData.category">
        <option disabled value="">請選擇分類</option>
        <option>自然</option>
        <option>文化</option>
        <option>美食</option>
        <option>購物</option>
        <option>其他</option>
      </select>
    </div>

    <div class="input-group">
      <label>地點 / 縣市</label>
      <input v-model="formData.location" placeholder="例如：新北" />
    </div>

    <div class="input-group">
      <label>營業時間</label>
      <input v-model="formData.hours" placeholder="例如：10:00-20:00 或 全天" />
    </div>

    <div class="input-group">
      <label>特色標籤 (用逗號隔開)</label>
      <input v-model="formData.featuresStr" placeholder="例如：老街, 小吃, 夜景" />
    </div>

    <div class="input-group">
      <label>推薦活動 (用逗號隔開)</label>
      <input v-model="formData.activitiesStr" placeholder="例如：茶館, 拍照, 健行" />
    </div>

    <button @click="submitData">送出資料</button>
  </div>
</template>

<style scoped>
.form-box {
  background: #eef; /* 淺藍色背景 */
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  text-align: center; /* 讓內容置中 */
  max-width: 500px;   /* 限制表單最大寬度 */
  margin: 0 auto 30px auto; /* 上下邊距，並置中 */
}

h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.input-group {
  margin-bottom: 15px;
  text-align: left; /* 標題文字靠左比較好讀 */
  width: 90%;       /* 寬度控制 */
  margin-left: auto;
  margin-right: auto;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  font-size: 0.9rem;
  color: #555;
}

input, select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* 確保 padding 不會撐破寬度 */
}

button {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 10px;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #45a049;
}
</style>