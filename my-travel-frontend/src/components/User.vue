<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

// 定義事件，讓 User.vue 可以通知 App.vue 換頁
const emit = defineEmits(['changePage'])

// --- 設定區 ---
const userId = localStorage.getItem('userId'); 
const API_URL = "http://localhost:8000"; 

// --- 常用國碼列表 ---
const countryCodes = [
  { code: '+886', label: '台灣 (+886)' },
  { code: '+86', label: '中國 (+86)' },
  { code: '+852', label: '香港 (+852)' },
  { code: '+81', label: '日本 (+81)' },
  { code: '+82', label: '韓國 (+82)' },
  { code: '+1', label: '美國 (+1)' },
  { code: '+44', label: '英國 (+44)' },
  { code: '+61', label: '澳洲 (+61)' },
  { code: '+65', label: '新加坡 (+65)' },
  { code: '+33', label: '法國 (+33)' },
  { code: '+49', label: '德國 (+49)' },
]

// --- 狀態變數 ---
const user = ref(null);
const loading = ref(true);
const error = ref(null);
const isEditing = ref(false);

const formData = reactive({
  name: '',
  phonePrefix: '+886', // 新增：國碼
  phoneNumber: '',     // 新增：電話號碼 (不含國碼)
  birthday: '',
  likes: {}
});

// --- 方法 ---

const fetchUser = async () => {
  if (!userId) {
    alert("您尚未登入，請先登入！");
    emit('changePage', 'login'); 
    return;
  }

  try {
    loading.value = true;
    error.value = null;
    const response = await axios.get(`${API_URL}/users/${userId}`);
    user.value = response.data;
  } catch (err) {
    console.error(err);
    error.value = "無法取得資料，請確認後端是否啟動。";
    
    if (err.response && (err.response.status === 404 || err.response.status === 401)) {
        localStorage.clear();
        alert("登入已過期，請重新登入");
        emit('changePage', 'login'); 
    }
  } finally {
    loading.value = false;
  }
};

const startEditing = () => {
  formData.name = user.value.name;
  
  // --- 處理電話號碼拆解邏輯 ---
  // 假設資料庫存的是 "+886912345678" 或純號碼 "0912345678"
  const fullPhone = user.value.phone || '';
  
  // 嘗試比對是否包含已知國碼
  const foundCode = countryCodes.find(c => fullPhone.startsWith(c.code));
  
  if (foundCode) {
    formData.phonePrefix = foundCode.code;
    formData.phoneNumber = fullPhone.replace(foundCode.code, '');
  } else {
    // 如果沒找到對應國碼 (或是舊資料沒有 +號)，預設給 +886，並保留原字串
    formData.phonePrefix = '+886';
    formData.phoneNumber = fullPhone;
  }

  // --- 處理生日 ---
  if (user.value.birthday) {
    formData.birthday = user.value.birthday.split('T')[0];
  } else {
    formData.birthday = '';
  }
  
  formData.likes = user.value.likes ? JSON.parse(JSON.stringify(user.value.likes)) : {};
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
};

const saveUser = async () => {
  try {
    // 組合國碼與電話
    const fullPhone = `${formData.phonePrefix}${formData.phoneNumber}`;

    const payload = {
      name: formData.name,
      phone: fullPhone, // 這裡送出完整的號碼
      birthday: formData.birthday ? new Date(formData.birthday).toISOString() : null,
      likes: formData.likes
    };

    const response = await axios.put(`${API_URL}/users/${userId}`, payload);
    
    user.value = response.data;
    isEditing.value = false;
    alert("更新成功！");
  } catch (err) {
    console.error(err);
    alert("更新失敗：" + (err.response?.data?.detail || err.message));
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '未設定';
  return new Date(dateString).toLocaleDateString();
};

onMounted(() => {
  fetchUser();
});
</script>

<template>
  <div class="user-profile-container">
    <h1>個人資料</h1>
    <div v-if="loading" class="loading">資料載入中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="!loading && user" class="profile-card">
      <div v-if="!isEditing">
        <div class="info-group"><label>Email：</label><span>{{ user.email }}</span></div>
        <div class="info-group"><label>姓名：</label><span>{{ user.name || '未設定' }}</span></div>
        <div class="info-group"><label>電話：</label><span>{{ user.phone || '未設定' }}</span></div>
        <div class="info-group"><label>生日：</label><span>{{ formatDate(user.birthday) }}</span></div>
        <div class="info-group">
          <label>喜好：</label>
          <div class="tags">
            <span v-for="(value, key) in user.likes" :key="key" class="tag">{{ key }}: {{ value }}</span>
          </div>
        </div>
        <button @click="startEditing" class="btn-primary">編輯資料</button>
      </div>

      <div v-else class="edit-form">
        <div class="form-group"><label>姓名</label><input v-model="formData.name" type="text" /></div>
        
        <div class="form-group">
          <label>電話</label>
          <div class="phone-input-group">
            <select v-model="formData.phonePrefix" class="phone-select">
              <option v-for="c in countryCodes" :key="c.code" :value="c.code">
                {{ c.label }}
              </option>
            </select>
            <input v-model="formData.phoneNumber" type="text" placeholder="請輸入號碼" class="phone-input" />
          </div>
        </div>

        <div class="form-group"><label>生日</label><input v-model="formData.birthday" type="date" /></div>
        <div class="form-group"><label>喜好 (Food)</label><input v-model="formData.likes.food" type="text" /></div>
        
        <div class="button-group">
          <button @click="saveUser" class="btn-save">儲存</button>
          <button @click="cancelEdit" class="btn-cancel">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-profile-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
  font-family: '微軟正黑體', Arial, sans-serif;
  color: var(--text-color); 
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  color: var(--text-color); 
}

.profile-card {
  background: var(--card-bg); 
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 10px var(--shadow-color); 
  border: 1px solid var(--border-color); 
}

.info-group, .form-group {
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color); 
  padding-bottom: 10px;
}

label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--text-secondary); 
}

span {
  color: var(--text-color); 
  font-size: 1.1rem;
}

input, select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--input-border); 
  border-radius: 6px;
  box-sizing: border-box;
  background-color: var(--input-bg); 
  color: var(--text-color); 
  transition: all 0.3s;
}

input:focus, select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

/* ⭐ 新增：電話輸入框組合樣式 */
.phone-input-group {
  display: flex;
  gap: 10px; /* 國碼和號碼中間的間距 */
}

.phone-select {
  width: 35%; /* 國碼選單寬度 */
  flex-shrink: 0;
}

.phone-input {
  flex-grow: 1; /* 號碼欄位佔滿剩餘空間 */
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background-color: var(--input-bg); 
  color: var(--primary-color);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  border: 1px solid var(--border-color);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  font-size: 1rem;
  font-weight: bold;
  transition: opacity 0.3s;
}

.btn-primary:hover {
  opacity: 0.9;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-save {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  flex: 1;
  cursor: pointer;
  font-weight: bold;
}

.btn-cancel {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  flex: 1;
  cursor: pointer;
  font-weight: bold;
}

.loading, .error {
  text-align: center;
  margin-top: 20px;
  font-size: 1.2rem;
  color: var(--text-secondary);
}

.error {
  color: #e74c3c;
}
</style>