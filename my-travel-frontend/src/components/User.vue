<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

// 定義事件，讓 User.vue 可以通知 App.vue 換頁
const emit = defineEmits(['changePage'])

// --- 設定區 ---
const userId = localStorage.getItem('userId'); 
const API_URL = "http://localhost:8000"; 

// --- 狀態變數 ---
const user = ref(null);
const loading = ref(true);
const error = ref(null);
const isEditing = ref(false);

const formData = reactive({
  name: '',
  phone: '',
  birthday: '',
  likes: {}
});

// --- 方法 ---

const fetchUser = async () => {
  // 檢查是否已登入
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
        emit('changePage', 'login'); // 通知換頁
    }
  } finally {
    loading.value = false;
  }
};

const startEditing = () => {
  formData.name = user.value.name;
  formData.phone = user.value.phone;
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
    const payload = {
      name: formData.name,
      phone: formData.phone,
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
        <div class="form-group"><label>電話</label><input v-model="formData.phone" type="text" /></div>
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
  color: var(--text-color); /* 改用變數 */
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  color: var(--text-color); /* 改用變數 */
}

.profile-card {
  background: var(--card-bg); /* 改用變數 */
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 10px var(--shadow-color); /* 改用變數 */
  border: 1px solid var(--border-color); /* 改用變數 */
}

.info-group, .form-group {
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color); /* 改用變數 */
  padding-bottom: 10px;
}

label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--text-secondary); /* 改用變數 */
}

span {
  color: var(--text-color); /* 改用變數 */
  font-size: 1.1rem;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--input-border); /* 改用變數 */
  border-radius: 6px;
  box-sizing: border-box;
  background-color: var(--input-bg); /* 改用變數 */
  color: var(--text-color); /* 改用變數 */
  transition: all 0.3s;
}

input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background-color: var(--input-bg); /* 改用變數 */
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