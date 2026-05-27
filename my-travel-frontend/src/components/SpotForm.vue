<script setup>

// 新增景點
import { ref, watch } from 'vue'
import api from '../api/axios.js'

const props = defineProps({
  spotToEdit: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submitSuccess', 'cancel'])
const formData = ref({
  name: '', category: '', region: '', location: '', hours: '', featuresStr: '', activitiesStr: ''
})

//  自動填寫魔法：只要發現有舊資料，就自動填入 formData
watch(() => props.spotToEdit, (newVal) => {
  if (newVal) {
    formData.value = {
      name: newVal.name || '',
      category: newVal.category || '',
      region: newVal.region || '',
      location: newVal.location || '',
      hours: newVal.hours || '',
      // 把陣列變回字串顯示在輸入框
      featuresStr: newVal.features?.features?.join(', ') || '',
      activitiesStr: newVal.activities?.activities?.join(', ') || ''
    }
  } else {
    // 如果沒有傳入舊資料，就清空表單 (代表是新增模式)
    formData.value = { name: '', category: '', region: '', location: '', hours: '', featuresStr: '', activitiesStr: '' }
  }
}, { immediate: true })

const nameError = ref('')     // 存放錯誤訊息
const isChecking = ref(false) // 是否正在檢查中

// 監聽名稱變化，進行檢查
const checkName = async (name) => {
  if (!name) {
    nameError.value = ''
    return
  }
  
  try {
    isChecking.value = true
    // 呼叫後端我們剛剛寫好的 check_name API
    const res = await api.get(`/api/spots/check_name/`, {
      params: { name }
    })
    
    // 根據後端回傳的資料判斷
    if (res.data.exists) {
      const names = res.data.similar_names.join(', ')
      
      // 如果完全一樣，顯示「已存在」
      if (res.data.similar_names.includes(name)) {
          nameError.value = '⚠️ 這個景點已經存在囉！'
      } else {
          // 如果只是類似，顯示「發現類似」
          nameError.value = `⚠️ 發現類似景點：${names}，確定要新增嗎？`
      }
    } else {
      nameError.value = '' // 通過檢查，清空錯誤
    }
  } catch (e) {
    console.error(e)
  } finally {
    isChecking.value = false
  }
}
let timeoutId = null

watch(() => formData.value.name, (newVal) => {
  // 先清空錯誤，讓使用者知道我們有在動作
  if (!newVal) {
      nameError.value = '';
      return;
  }
  
  // 清除上一次的計時器
  if (timeoutId) clearTimeout(timeoutId)
  
  // 設定新的計時器
  timeoutId = setTimeout(() => {
    checkName(newVal)
  }, 500) // 0.5 秒後執行
})

const submitData = async () => {
  // 完全重複的名稱不允許新增
  if (nameError.value.includes('已經存在')) {
      alert("此景點已存在，請勿重複新增！")
      return
  }

  // 如果有類似名稱，跳出確認視窗
  if (nameError.value.includes('發現類似')) {
      // 跳出確認視窗，如果使用者按「取消」，就擋下
    const isConfirmed = confirm(`${nameError.value}\n\n(如果您確定這是不同的新景點，請按「確定」繼續)`)
    if (!isConfirmed) {
        return
    }
  }
  // 基本防呆
  if (!formData.value.name.trim() || !formData.value.category || !formData.value.location.trim()) {
    alert('❌ 請填寫所有必填欄位 (名稱、分類、地點)！')
    return
  }

  try {
    const featuresJson = formData.value.featuresStr.split(/[,，]/).map(s => s.trim()).filter(s => s)
    const activitiesJson = formData.value.activitiesStr.split(/[,，]/).map(s => s.trim()).filter(s => s)

    const payload = {
      name: formData.value.name,
      category: formData.value.category,
      region: formData.value.region,
      location: formData.value.location,
      hours: formData.value.hours,
      features: featuresJson,
      activities: activitiesJson
    }

    // 判斷是新增還是編輯
    if (props.spotToEdit) {
      // 編輯模式：打 PUT API (記得帶上 id)
      await api.put(`/api/spots/${props.spotToEdit.id}/`, payload)
      alert('✏️ 更新成功！')
    } else {
      // 新增模式：打 POST API
      await api.post('/api/spots/', payload)
      alert('🎉 新增成功！')
    }
    
    // 清空並通知老爸
    formData.value = { name: '', category: '', region: '', location: '', hours: '', featuresStr: '', activitiesStr: '' }
    emit('submitSuccess')// 通知父元件新增成功
  } catch (error) {
    if (error.response && error.response.status === 400) {
        // 這會顯示後端回傳的 "這個景點已經存在囉！"
        alert(`❌ 新增失敗：${error.response.data.detail}`) 
    } else {
        alert('❌ 新增失敗，請檢查後端')
        console.error(error)
    }
  }
}
</script>

<template>
  <div class="form-container">
    <div class="form-box">
      <div class="form-header">
        <h3>{{ spotToEdit ? '✏️ 編輯景點' : '➕ 新增私房景點' }}</h3>
        <p>{{ spotToEdit ? '協助更新最新的景點資訊' : '分享你發現的美好角落' }}</p>
      </div>
      
      <div class="input-group">
        <label>景點名稱 <span class="required">*</span></label>
        <input 
          v-model="formData.name" 
          placeholder="例如：九份老街" 
          required
          :class="{ 'input-error': nameError }"
        />

        <span v-if="isChecking" class="checking-msg">🔍 檢查中...</span>
        <span v-if="nameError" class="error-msg">{{ nameError }}</span>
      </div>

      <div class="input-group">
        <label>分類 <span class="required">*</span></label>
        <select v-model="formData.category" required>
          <option disabled value="">請選擇分類</option>
          
          <optgroup label="景點類型">
            <option>自然生態</option>
            <option>歷史人文</option>
            <option>在地美食</option>
            <option>休閒娛樂</option>
            <option>購物商圈</option>
            <option>網美打卡</option>
          </optgroup>

          <option value="其他">✨ 其他</option>
        </select>
      </div>

      <div class="input-group half">
        <label>🌍 所屬洲際 <span class="required">*</span></label>
        <select v-model="formData.region" required>
          <option disabled value="">請選擇所屬洲際</option>
          <option value="Asia">亞洲(不含台灣)</option>
          <option value="Europe">歐洲</option>
          <option value="Americas">美洲</option>
          <option value="Oceania">大洋洲</option>
          <option value="Africa">非洲</option>
          <option value="Taiwan">台灣</option>
        </select>
      </div>

      <div class="input-group half">
        <label>📍 詳細地點 <span class="required">*</span></label>
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

      <button @click="submitData" class="submit-btn">
        {{ spotToEdit ? '儲存更新' : '送出資料' }}
      </button>
      
      <button v-if="spotToEdit" @click="emit('cancel')" class="submit-btn" style="background-color: #999; margin-top: 10px;">
        取消編輯
      </button>
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

.input-error {
  border-color: #ff4d4f !important;
  background-color: #fff1f0 !important;
}

.error-msg {
  color: #ff4d4f;
  font-size: 0.9rem;
  margin-top: 5px;
  display: block;
  font-weight: bold;
}

.checking-msg {
  color: #1890ff;
  font-size: 0.9rem;
  margin-top: 5px;
  display: block;
}
</style>