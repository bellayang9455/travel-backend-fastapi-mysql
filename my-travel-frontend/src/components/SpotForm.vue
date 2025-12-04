<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 定義表單資料
const formData = ref({
  name: '',
  description: '',
  address: ''
})

const submitData = async () => {
  try {
    // ⚠️ 發送 POST 請求給後端
    await axios.post('http://127.0.0.1:8000/spots', formData.value)
    alert('新增成功！')
    // 新增完清空表單
    formData.value = { name: '', description: '', address: '' }
    // 這裡通常會通知列表重新整理 (為了簡單先省略)
  } catch (error) {
    alert('新增失敗，請檢查後端')
    console.error(error)
  }
}
</script>

<template>
  <div class="form-box">
    <h3>➕ 新增私房景點</h3>
    <div class="input-group">
      <input v-model="formData.name" placeholder="景點名稱 (例如：台北101)" />
    </div>
    <div class="input-group">
      <input v-model="formData.description" placeholder="介紹一下這個地方..." />
    </div>
    <div class="input-group">
      <input v-model="formData.address" placeholder="地址" />
    </div>
    <button @click="submitData">送出資料</button>
  </div>
</template>

<style scoped>
.form-box {
  background: rgb(118, 175, 183);
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 30px;
}
.input-group {
  margin-bottom: 10px;
}
input {
  width: 80%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background-color: #45a049;
}
</style>