<script setup>
import { ref } from 'vue'
import axios from 'axios'

const formData = ref({
  name: '',
  category: '',
  location: '',
  hours: '',
  featuresStr: '',
  activitiesStr: ''
})

const submitData = async () => {
  // ⭐ 防線 1：JavaScript 檢查
  // 檢查必填欄位是否為空 (trim() 去除前後空白)
  if (!formData.value.name.trim() || 
      !formData.value.category || 
      !formData.value.location.trim()) {
    
    alert('❌ 請填寫所有必填欄位 (名稱、分類、地點)！')
    return // ⛔ 程式停在這裡，不繼續往下跑
  }

  try {
    // 資料轉換：把逗號分隔的字串轉成 JSON 格式
    const featuresJson = {
      features: formData.value.featuresStr.split(/[,，]/).map(s => s.trim()).filter(s => s)
    }
    
    const activitiesJson = {
      activities: formData.value.activitiesStr.split(/[,，]/).map(s => s.trim()).filter(s => s)
    }

    const payload = {
      name: formData.value.name,
      category: formData.value.category,
      location: formData.value.location,
      hours: formData.value.hours,
      features: featuresJson,
      activities: activitiesJson
    }

    await axios.post('http://127.0.0.1:8000/spots', payload)
    
    alert('🎉 新增成功！')
    
    // 清空表單
    formData.value = {
      name: '', category: '', location: '', hours: '', featuresStr: '', activitiesStr: ''
    }
    
  } catch (error) {
    alert('❌ 新增失敗，請檢查後端')
    console.error(error)
  }
}
</script>

<template>
  <div class="form-container">
    <div class="form-box">
      <div class="form-header">
        <h3>➕ 新增私房景點</h3>
        <p>分享你發現的美好角落</p>
      </div>
      
      <div class="input-group">
        <label>景點名稱 <span class="required">*</span></label>
        <input 
          v-model="formData.name" 
          placeholder="例如：九份老街" 
          required
        />
      </div>

      <div class="input-group">
        <label>分類 <span class="required">*</span></label>
        <select v-model="formData.category" required>
          <option disabled value="">請選擇分類</option>
          <option>自然</option>
          <option>文化</option>
          <option>美食</option>
          <option>購物</option>
          <option>其他</option>
        </select>
      </div>

      <div class="input-group">
        <label>地點 / 縣市 <span class="required">*</span></label>
        <input 
          v-model="formData.location" 
          placeholder="例如：新北" 
          required
        />
      </div>

      <div class="input-group">
        <label>營業時間 (選填)</label>
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

      <button @click="submitData" class="submit-btn">送出資料</button>
    </div>
  </div>
</template>

<style scoped>
.form-container {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.form-box {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08); /* 漂亮的陰影 */
  width: 100%;
  max-width: 500px;
  border: 1px solid #eee;
}

.form-header {
  text-align: center;
  margin-bottom: 25px;
}

.form-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.form-header p {
  color: #888;
  font-size: 0.9rem;
  margin-top: 5px;
}

.input-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
  font-size: 0.95rem;
}

/* 紅色星號樣式 */
.required {
  color: #ff4d4f;
  margin-left: 4px;
}

input, select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px; /* 圓角 */
  font-size: 1rem;
  box-sizing: border-box; /* 確保不會撐破 */
  transition: border-color 0.3s;
}

input:focus, select:focus {
  outline: none;
  border-color: #4CAF50; /* 點擊時變綠色 */
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.submit-btn {
  width: 100%;
  background-color: #4CAF50; /* 綠色按鈕 */
  color: white;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
  margin-top: 10px;
}

.submit-btn:hover {
  background-color: #43a047;
}

.submit-btn:active {
  transform: scale(0.98); /* 點擊時縮小一點點 */
}
</style>