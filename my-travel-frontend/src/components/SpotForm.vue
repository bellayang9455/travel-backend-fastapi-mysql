<script setup>
import { ref } from 'vue'
import api from '../api/axios.js'

const emit = defineEmits(['submitSuccess'])

const formData = ref({
  name: '',
  category: '',
  location: '',
  hours: '',
  featuresStr: '',
  activitiesStr: ''
})

const submitData = async () => {
  if (!formData.value.name.trim() || !formData.value.category || !formData.value.location.trim()) {
    alert('❌ 請填寫所有必填欄位 (名稱、分類、地點)！')
    return
  }

  try {
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
    
    emit('submitSuccess') // 通知父元件新增成功
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
          
          <optgroup label="景點類型">
            <option>🏞️ 自然生態</option>
            <option>🏯 歷史人文</option>
            <option>🍜 在地美食</option>
            <option>🎡 休閒娛樂</option>
            <option>🛍️ 購物商圈</option>
            <option>📸 網美打卡</option>
          </optgroup>

          <optgroup label="住宿類型">
            <option value="飯店">🏨 飯店</option>
            <option value="民宿">🏩 民宿</option>
            <option value="露營">🏕️ 露營</option>
            <option value="青旅">🛏️ 青年旅館</option>
            <option value="公寓式住宿">🏠 公寓式住宿</option>
          </optgroup>

          <option value="其他">✨ 其他</option>
        </select>
      </div>

      <div class="input-group half">
        <label>地點 <span class="required">*</span></label>
        <input 
          v-model="formData.location" 
          placeholder="例如：新北" 
          required
        />
      </div>

      <div class="input-group half">
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
  background: var(--card-bg); /* 改用變數 */
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 30px var(--shadow-color); /* 改用變數 */
  border: 1px solid var(--border-color); /* 改用變數 */
  width: 100%;
  max-width: 1000px; 
  color: var(--text-color); /* 改用變數 */
  transition: all 0.3s;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 20px;
}

.form-header h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.8rem;
}

.form-header p {
  color: var(--text-secondary);
  margin-top: 8px;
}

.input-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
  color: var(--text-color);
}

/* 紅色星號樣式 */
.required {
  color: #ff4d4f;
  margin-left: 4px;
}

input, select {
  width: 100%;
  padding: 15px;
  border: 1px solid var(--input-border); /* 改用變數 */
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  background-color: var(--input-bg); /* 改用變數 */
  color: var(--text-color); /* 改用變數 */
  transition: all 0.3s;
}

input:focus, select:focus {
  outline: none;
  background-color: var(--card-bg);
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.1);
}

.submit-btn {
  width: 100%;
  background-color: var(--primary-color);
  color: white;
  padding: 16px;
  border: none;
  border-radius: 8px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 20px;
  transition: opacity 0.3s;
  letter-spacing: 2px;
}

.submit-btn:hover {
  opacity: 0.9;
}
</style>