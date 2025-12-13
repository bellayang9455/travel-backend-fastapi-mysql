<script setup>
import { ref } from 'vue';
import axios from 'axios';

// 定義事件：用來通知 App.vue 切換頁面
const emit = defineEmits(['registerSuccess', 'changePage'])

// 註冊表單資料
const registerData = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const isLoading = ref(false);

const handleRegister = async () => {
  // 1. 前端驗證
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
    
    // 2. 呼叫後端註冊 API
    // 這裡會把資料送到 FastAPI 的 /register
    const payload = {
      email: registerData.value.email,
      password: registerData.value.password,
      name: registerData.value.name
    };

    // 呼叫 API
    await axios.post('http://localhost:8000/register', payload);

    alert(`🎉 註冊成功！歡迎 ${registerData.value.name} 加入！`);
    
    // 3. 成功後，通知父元件切換到登入頁
    emit('registerSuccess');
    
  } catch (error) {
    console.error(error);
    if (error.response && error.response.data && error.response.data.detail) {
      alert('❌ 註冊失敗：' + error.response.data.detail);
    } else {
      alert('❌ 註冊失敗，請檢查後端是否啟動');
    }
  } finally {
    isLoading.value = false;
  }
};
</script>