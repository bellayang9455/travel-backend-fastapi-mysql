<script setup>
// 關於使用者登入

// 匯入
import { ref } from 'vue'
import api from '../api/axios.js'

// 定義可以發送的事件，對應 App.vue 裡的 @loginSuccess
const emit = defineEmits(['loginSuccess'])

// 資料
const loginData = ref({
  email: '',
  password: ''
})

const isLoading = ref(false)


// 登入檢查
const handleLogin = async () => {
  // 1. 基本防呆
  if (!loginData.value.email || !loginData.value.password) {
    alert('❌ 請輸入帳號與密碼！')
    return
  }

  try {
    isLoading.value = true
    
    // 2. 呼叫後端 API
    const response = await api.post('/auth/login', {
      email: loginData.value.email,
      password: loginData.value.password
    })

    // 3. 取得後端回傳的資料
    const { access_token, user_id, user_name } = response.data

    // 4. [關鍵] 將 userId 存入 localStorage
    // 這樣 User.vue 就能讀取到這個 ID，不用再寫死了
    const userData = {
      id: user_id,
      name: user_name,
      email: loginData.value.email
    }

    // 儲存到 localStorage
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))

    // 清除舊的單獨存的資料（如果有的話）
    localStorage.removeItem('userId') 
    localStorage.removeItem('userName')


    alert(`🎉 歡迎回來，${user_name}！`)
    
    // 5. 發送事件通知 App.vue 切換頁面
    emit('loginSuccess',userData)
    
  } catch (error) {
    console.error(error)
    
    if (error.response && error.response.status === 400) {
      alert('❌ 登入失敗：帳號或密碼錯誤')
    } else {
      alert('❌ 登入失敗，請確認後端是否啟動')
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="form-container">
    <div class="form-box">
      <div class="form-header">
        <h3>🔑 會員登入</h3>
        <p>歡迎回來，繼續您的旅程規劃</p>
      </div>

      <div class="input-group">
        <label>電子信箱</label>
        <input 
          v-model="loginData.email" 
          type="email" 
          placeholder="example@email.com" 
          required 
          @keyup.enter="handleLogin"
        />
      </div>

      <div class="input-group">
        <label>密碼</label>
        <input 
          v-model="loginData.password" 
          type="password" 
          placeholder="請輸入密碼" 
          required 
          @keyup.enter="handleLogin"
        />
      </div>

      <button @click="handleLogin" class="submit-btn" :disabled="isLoading">
        {{ isLoading ? '登入中...' : '登入' }}
      </button>
      </div>
  </div>
</template>

<style scoped>
/* 樣式保持與 RegisterForm 一致 */
.form-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  margin-top: 50px;
}

.form-box {
  background: var(--card-bg, #ffffff);
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 30px var(--shadow-color, rgba(0,0,0,0.1));
  border: 1px solid var(--border-color, #eee);
  width: 100%;
  max-width: 400px;
  color: var(--text-color, #333);
  transition: all 0.3s;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-header h3 {
  margin: 0;
  font-size: 1.8rem;
  color: var(--text-color, #2c3e50);
}

.form-header p {
  color: var(--text-secondary, #7f8c8d);
  margin-top: 8px;
}

.input-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: var(--text-color, #2c3e50);
}

input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid var(--input-border, #ddd);
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  background-color: var(--input-bg, #fff);
  color: var(--text-color, #333);
  transition: all 0.3s;
}

input:focus {
  outline: none;
  border-color: var(--primary-color, #4CAF50);
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.submit-btn {
  width: 100%;
  background-color: var(--primary-color, #4CAF50);
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
</style>