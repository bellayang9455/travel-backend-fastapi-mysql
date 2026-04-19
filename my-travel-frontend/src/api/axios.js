// src/api/axios.js
// 專門用來設定 axios 的檔案
import axios from 'axios';

// 1. 建立一個專用的 api 實例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 後端的網址
  timeout: 200000, // 可選的請求超時設定
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2.【請求攔截器】自動帶上 Token
api.interceptors.request.use(
  (config) => {
    // 從 localStorage 拿出 token
    const token = sessionStorage.getItem('token');
    /*const token = localStorage.getItem('token');*/
    // 如果有 token，就把它加到 Header 裡
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3.【回應攔截器】處理 Token 過期 (401 錯誤)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      console.log('Token 過期，強制登出');
      
      // ✅ 改成全面清除 sessionStorage
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user_name');
      sessionStorage.removeItem('user_id');
      
      // 💡 或者是更霸氣的寫法：直接清空當前分頁的所有 session 資料
      // sessionStorage.clear(); 

      // 強制重新整理頁面
      window.location.href = '/login'; 
    }
    return Promise.reject(error);
  }
);

// 匯出這個設定好的 api
export default api;