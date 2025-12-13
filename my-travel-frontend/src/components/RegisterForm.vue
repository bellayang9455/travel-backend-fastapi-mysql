<script setup>
import { ref, watch } from 'vue'; // 引入 watch
import axios from 'axios';

const emit = defineEmits(['registerSuccess', 'changePage'])

const registerData = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
});

// --- 檢查名字相關狀態 ---
const isChecking = ref(false);      // 是否正在檢查中 (轉圈圈)
const nameAvailable = ref(null);    // null=未檢查, true=可用(綠色), false=不可用(紅色)
const nameMsg = ref('');            // 顯示的訊息
let checkTimeout = null;            // 用來計時的變數

// 監聽名字輸入，即時檢查
const handleNameInput = () => {
  // 1. 重置狀態
  nameAvailable.value = null;
  nameMsg.value = '';
  
  // 2. 如果清空了，就不檢查
  if (!registerData.value.name) return;

  // 3. 顯示轉圈圈
  isChecking.value = true;

  // 4. 清除上一次的計時 (防手抖機制)
  if (checkTimeout) clearTimeout(checkTimeout);

  // 5. 設定新的計時：使用者停下來 500ms 後才發送請求
  checkTimeout = setTimeout(async () => {
    try {
      // 呼叫剛剛寫好的後端 API
      const response = await axios.get(`http://localhost:8000/check_name/${registerData.value.name}`);
      
      if (response.data.exists) {
        nameAvailable.value = false;
        nameMsg.value = '❌ 這個名字已經有人用了';
      } else {
        nameAvailable.value = true;
        nameMsg.value = '✅ 這個名字可以用';
      }
    } catch (error) {
      console.error(error);
    } finally {
      // 檢查結束，關閉轉圈圈
      isChecking.value = false;
    }
  }, 500); // 0.5秒
};

const isLoading = ref(false);

const handleRegister = async () => {
  // 註冊前再防呆一次
  if (nameAvailable.value === false) {
    alert('❌ 請更換使用者名稱！');
    return;
  }

  if (!registerData.value.name || !registerData.value.email || !registerData.value.password) {
    alert('❌ 請填寫所有欄位！');
    return;
  }
  
  if (registerData.value.password !== registerData.value.confirmPassword) {
    alert('❌ 兩次密碼輸入不一致！');
    return;
  }

  try {
    isLoading.value = true;
    const payload = {
      email: registerData.value.email,
      password: registerData.value.password,
      name: registerData.value.name
    };

    await axios.post('http://localhost:8000/register', payload);

    alert(`🎉 註冊成功！歡迎 ${registerData.value.name} 加入！`);
    emit('registerSuccess'); 
    
  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail) {
      alert('❌ 註冊失敗：' + error.response.data.detail);
    } else {
      alert('❌ 註冊失敗，請確認後端是否啟動');
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="form-container">
    <div class="form-box">
      <div class="form-header">
        <h3>✨ 加入我們</h3>
        <p>建立帳號，開始紀錄您的旅程</p>
      </div>

      <div class="input-group">
        <label>使用者名稱 <span class="required">*</span></label>
        
        <div class="input-wrapper">
          <input 
            v-model="registerData.name" 
            @input="handleNameInput" 
            type="text" 
            placeholder="怎麼稱呼您？" 
            :class="{ 'input-error': nameAvailable === false, 'input-success': nameAvailable === true }"
            required 
          />
          
          <span class="status-icon">
            <span v-if="isChecking" class="spinner">🌀</span>
            <span v-else-if="nameAvailable === true" class="fade-in">✅</span>
            <span v-else-if="nameAvailable === false" class="fade-in">❌</span>
          </span>
        </div>
        <small class="status-msg" :class="{ 'error-text': !nameAvailable, 'success-text': nameAvailable }">
          {{ nameMsg }}
        </small>
      </div>

      <div class="input-group">
        <label>電子信箱 <span class="required">*</span></label>
        <input v-model="registerData.email" type="email" placeholder="example@email.com" required />
      </div>

      <div class="input-group">
        <label>密碼 <span class="required">*</span></label>
        <input v-model="registerData.password" type="password" placeholder="請輸入密碼" required />
      </div>

      <div class="input-group">
        <label>確認密碼 <span class="required">*</span></label>
        <input v-model="registerData.confirmPassword" type="password" placeholder="再次輸入密碼" required />
      </div>

      <button @click="handleRegister" class="submit-btn" :disabled="isLoading || nameAvailable === false">
        {{ isLoading ? '處理中...' : '立即註冊' }}
      </button>
      
      <p class="login-link">
        已有帳號？ 
        <a href="#" @click.prevent="$emit('changePage', 'login')">直接登入</a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.form-container { display: flex; justify-content: center; padding: 20px; margin-top: 50px; }
.form-box { background: var(--card-bg); padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px var(--shadow-color); border: 1px solid var(--border-color); width: 100%; max-width: 500px; color: var(--text-color); transition: all 0.3s; }
.form-header { text-align: center; margin-bottom: 30px; }
.form-header h3 { margin: 0; color: var(--text-color); font-size: 1.8rem; }
.form-header p { color: var(--text-secondary); margin-top: 8px; }

.input-group { margin-bottom: 20px; }
label { display: block; margin-bottom: 8px; font-weight: bold; color: var(--text-color); }
.required { color: #e74c3c; margin-left: 4px; }

/* 輸入框與 Icon 的容器 */
.input-wrapper { position: relative; }

input { width: 100%; padding: 12px 15px; padding-right: 40px; /* 右邊留空間給 Icon */ border: 1px solid var(--input-border); border-radius: 8px; font-size: 1rem; box-sizing: border-box; background-color: var(--input-bg); color: var(--text-color); transition: all 0.3s; }
input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1); }

/* 狀態框線顏色 */
.input-error { border-color: #e74c3c !important; box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1) !important; }
.input-success { border-color: #2ecc71 !important; box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1) !important; }

/* 狀態 Icon 位置 */
.status-icon { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font-size: 1.2rem; }

/* 轉圈圈動畫 */
.spinner { display: inline-block; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* 顯示動畫 */
.fade-in { animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.5); } to { opacity: 1; transform: scale(1); } }

/* 提示文字 */
.status-msg { display: block; margin-top: 5px; font-size: 0.85rem; height: 1.2em; }
.error-text { color: #e74c3c; }
.success-text { color: #2ecc71; }

.submit-btn { width: 100%; background-color: var(--primary-color); color: white; padding: 14px; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: bold; cursor: pointer; margin-top: 10px; transition: opacity 0.3s; }
.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; background-color: #ccc; }
.submit-btn:hover:not(:disabled) { opacity: 0.9; }

.login-link { text-align: center; margin-top: 20px; font-size: 0.9rem; color: var(--text-secondary); }
.login-link a { color: var(--primary-color); text-decoration: none; font-weight: bold; }
</style>