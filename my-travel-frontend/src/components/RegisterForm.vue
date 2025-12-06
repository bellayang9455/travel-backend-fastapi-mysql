<script setup>
import { ref } from 'vue'
import axios from 'axios'

const registerData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const isLoading = ref(false)

const handleRegister = async () => {
  // 1. 前端驗證
  if (!registerData.value.username || !registerData.value.email || !registerData.value.password) {
    alert('❌ 請填寫所有欄位！')
    return
  }
  
  if (registerData.value.password !== registerData.value.confirmPassword) {
    alert('❌ 兩次密碼輸入不一致！')
    return
  }

  try {
    isLoading.value = true
    
    //假設後端有 /register API (目前先模擬成功)
    /axios.post('http://127.0.0.1:8000/register', {
      username: registerData.value.username,
      email: registerData.value.email,
      password: registerData.value.password
    })

    // 模擬網路延遲
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    alert(`🎉 註冊成功！歡迎 ${registerData.value.username} 加入旅遊日記！`)
    // 這裡通常會自動跳轉到登入頁或首頁
    
  } catch (error) {
    alert('❌ 註冊失敗，請稍後再試')
    console.error(error)
  } finally {
    isLoading.value = false
  }
}
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
        <input v-model="registerData.username" type="text" placeholder="怎麼稱呼您？" required />
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

      <button @click="handleRegister" class="submit-btn" :disabled="isLoading">
        {{ isLoading ? '處理中...' : '立即註冊' }}
      </button>
      
      <p class="login-link">
        已有帳號？ <a href="#">直接登入</a>
      </p>
    </div>
  </div>
</template>

<style scoped>
/* 沿用 SpotForm 的設計風格 */
.form-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  margin-top: 50px;
}

.form-box {
  background: var(--card-bg);
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 30px var(--shadow-color);
  border: 1px solid var(--border-color);
  width: 100%;
  max-width: 500px; /* 註冊表單窄一點比較好看 */
  color: var(--text-color);
  transition: all 0.3s;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
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
  margin-bottom: 8px;
  font-weight: bold;
  color: var(--text-color);
}

.required {
  color: #e74c3c;
  margin-left: 4px;
}

input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid var(--input-border);
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  background-color: var(--input-bg);
  color: var(--text-color);
  transition: all 0.3s;
}

input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.submit-btn {
  width: 100%;
  background-color: var(--primary-color);
  color: white;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
  transition: opacity 0.3s;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.login-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: bold;
}
</style>