<script setup>
// 關於上方選單列的邏輯

// 匯入
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios.js'

// 屬性與事件
const props = defineProps({
  activePage: String,
  isDarkMode: Boolean,
  userName: String, //接收來自 App.vue 的使用者名稱
  userId: String
})

// 定義要發出的事件
const emit = defineEmits([
  'changePage', 
  'filterLocation', 
  'filterCategory',  
  'toggleTheme',
  'selectCategory',
  'logout',
  'openLogin',  
  'openRegister',
  'loginSuccess', 
  'changePage'
])

// 變數
const router = useRouter(); // 取得 router 實例
const searchQuery = ref(''); // 搜尋關鍵字

// 狀態變數
const isLoggedIn = computed(() => !!props.userName)
const inviteCode = ref('')// 行程邀請碼的變數

// 側邊欄變數
const isSidebarOpen = ref(false)

// 行程協作加入
const handleJoinTrip = async () => {
  if (!inviteCode.value) return alert('請輸入邀請碼')
  if (!props.userId) {
      alert('請先登入才能加入行程！')
      router.push({ name: 'login' })
      return
  }// 防呆
  
  try {
    // 2. 呼叫後端加入行程 API
    // 注意：api.post 會自動帶上 Token
    const res = await api.post(`/api/collab/join/${inviteCode.value}`,{
      user_id: props.userId
    })
    
    alert(`🎉 ${res.data.message}`)
    inviteCode.value = '' // 清空輸入框
    
    router.push({ name: 'user' }) // 跳轉到個人頁面查看
  } catch (error) {
    console.error(error)
    const msg = error.response?.data?.detail || '加入失敗'
    alert(`❌ ${msg}`)
  }
}

// 下拉選單資料 
const locations = [
  { name: '亞洲(不含台灣)', value: 'Asia' },
  { name: '歐洲', value: 'Europe' },
  { name: '美洲', value: 'Americas' },
  { name: '大洋洲', value: 'Oceania' },
  { name: '非洲', value: 'Africa' },
  { name: '台灣', value: 'Taiwan' }
]

const categories = [
  { name: '🏞️ 自然生態', value: '自然生態' },
  { name: '🏯 歷史人文', value: '歷史人文' },
  { name: '🍜 在地美食', value: '在地美食' },
  { name: '🎡 休閒娛樂', value: '休閒娛樂' },
  { name: '🛍️ 購物商圈', value: '購物商圈' },
  { name: '📸 網美打卡', value: '網美打卡' },
  { name: '✨ 其他', value: '其他' }
]

// 方法
// 登出功能
const handleLogout = () => {
  if (confirm('確定要登出嗎？')) {
    // 1. 清除 localStorage
    /*localStorage.removeItem('token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_name')*/
    
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('user_id')
    sessionStorage.removeItem('user_name')
    // 2. 跳轉回登入頁或首頁
    emit('logout')
    
    alert('已成功登出')
    
    if (props.activePage !== 'home') {
       emit('changePage', 'home')
    }
  }
}

// 處理搜尋功能
const handleSearch = () => {
  if (!searchQuery.value.trim()) return;
  
  // 跳轉到首頁，並帶上 query 參數 (例如 /?q=台北)
  router.push({ 
    name: 'home', // 請確認你的路由設定首頁名稱是不是叫 'home' (或是 path: '/')
    query: { q: searchQuery.value } 
  });
  
  // 搜尋後清空框框
  searchQuery.value = ''; 
};

// 側邊欄切換
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

// 側邊欄 關閉 (點擊遮罩或選單項目後)
const handleMenuClick = (pageName) => {
  emit('changePage', pageName)
  isSidebarOpen.value = false
} 

// 篩選功能 (洲際、景點分類類型)
const handleFilterClick = (type, value) => {
  if (type === 'location') emit('filterLocation', value)
  if (type === 'category') emit('selectCategory', value)
  
  //emit('changePage', 'home') // 切回首頁看結果
  isSidebarOpen.value = false // 關閉側邊欄
}
</script>

// 更改成選單 + 側邊欄的設計
<template>
  <div class="nav-container">

    <header class="topbar">
      <div class="topbar-left">
        <button class="hamburger-btn" @click="toggleSidebar">☰</button>

        <div class="logo-area" @click="handleMenuClick('home')">
          <span class="icon">✈️</span>
          <span class="title">旅遊GO GO GO!</span>
        </div>
      </div>

      <div class="topbar-right">
        <div class="search-bar">
          <input v-model="searchQuery" @keyup.enter="handleSearch" placeholder="搜尋景點..." />
          <button @click="handleSearch">🔍</button>
        </div>

        <button class="theme-btn" @click="emit('toggleTheme')" title="切換風格">
          {{ isDarkMode ? '🌙' : '☀️' }}
        </button>

        <div class="header-right">
          <template v-if="isLoggedIn">
            <button class="user-info"
            @click="emit('changePage', 'user')"
            title="查看個人資料">
            👤 {{ props.userName }}
          </button>
            <button class="logout-btn-small" @click="handleLogout" title="登出">登出🚪</button>
          </template>
          <template v-else>
            <div class="auth-buttons">
              <button class="auth-btn login" @click="emit('openLogin')">登入 / 註冊</button>
            </div>
          </template>
        </div>
      </div>
    </header>

    <aside class="sidebar" :class="{'is-open' : isSidebarOpen}">
      <div class="sidebar-header">
        <button class="hamburger-toggle-btn" @click="toggleSidebar">☰</button>
      </div>
      <div class="sidebar-section" v-if="isLoggedIn">
        <div class="join-trip-box">
          <input v-model="inviteCode" placeholder="輸入邀請碼加入行程" @keyup.enter="handleJoinTrip" />
          <button @click="handleJoinTrip" title="加入行程">加入</button>
        </div>
      </div>

      <nav class="sidebar-nav">
        
        <a class="nav-item ai-btn" :class="{ active: activePage === 'ai_planner' }" @click="handleMenuClick('ai_planner')">
          ✨ AI 行程規劃
        </a>

        <a class="nav-item" :class="{ active: activePage === 'home' }" @click="handleMenuClick('home')">
          🏠 首頁列表
        </a>
        
        <a class="nav-item" :class="{ active: activePage === 'add' }" @click="handleMenuClick('add')">
          📍 新增景點
        </a>

        <a class="nav-item" v-if="isLoggedIn" :class="{ active: activePage === 'user' }" @click="handleMenuClick('user')">
          📅 我的行程 / 個人資料
        </a>

        <details class="nav-details">
          <summary class="nav-item">🌍 探索地點</summary>
          <div class="details-content">
            <a @click="handleFilterClick('location', '')">全部地點</a>
            <a v-for="loc in locations" :key="loc.value" @click="handleFilterClick('location', loc.value)">
              {{ loc.name }}
            </a>
          </div>
        </details>

        <details class="nav-details">
          <summary class="nav-item">🏷️ 景點分類</summary>
          <div class="details-content">
            <a @click="handleFilterClick('category', '全部')">所有分類</a>
            <a v-for="cat in categories" :key="cat.value" @click="handleFilterClick('category', cat.value)">
              {{ cat.name }}
            </a>
          </div>
        </details>
      </nav>
    </aside>
  </div>
</template>


<style scoped>
/* 頂部列樣式 */
.topbar {
  background-color: var(--nav-bg);
  box-shadow: 0 2px 10px var(--shadow-color);
  position: fixed; top: 0; left: 0; width: 100%; height: 60px; z-index: 50;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 20px; box-sizing: border-box;
}

.topbar-left, .topbar-right {
  display: flex; align-items: center; gap: 15px;
}

.hamburger-btn {
  font-size: 24px; background: none; border: none; cursor: pointer;
  color: var(--text-color); padding: 5px; border-radius: 4px; transition: 0.2s;
  margin: 0; display: flex; align-items: center;
}
.hamburger-btn:hover { background-color: var(--bg-color); }

.logo-area { display: flex; align-items: center; gap: 8px; cursor: pointer; user-select: none; }
.logo-area .icon { font-size: 24px; }
.logo-area .title { font-size: 20px; font-weight: bold; color: var(--text-color); }

.search-bar { display: flex; align-items: center; background: var(--bg-color); border-radius: 20px; padding: 5px 15px; border: 1px solid var(--border-color);}
.search-bar input { border: none; background: transparent; outline: none; color: var(--text-color); width: 150px; }
.search-bar button { background: none; border: none; cursor: pointer; }

.theme-btn {
  background: none; border: 1px solid var(--border-color); border-radius: 50%;
  width: 36px; height: 36px; cursor: pointer; font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-color); transition: 0.3s;
}
.theme-btn:hover { background-color: var(--bg-color); transform: rotate(15deg); }

/* 側邊欄樣式 */
.sidebar {
  position: fixed; top: 0; left: 0; width: 280px; height: 100vh;
  background-color: var(--nav-bg); box-shadow: 2px 0 10px rgba(0,0,0,0.1);
  z-index: 100; display: flex; flex-direction: column;
  transform: translateX(-100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto; /* 內容太多可捲動 */
}

.sidebar.is-open { 
  transform: translateX(0); 
}

.hamburger-toggle-btn {
  background: none;
  border: none;
  font-size: 24px; 
  color: var(--text-color);
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s;
  margin: 0;
  margin-right: 15px; 
  display: flex;
  align-items: center;
}

.hamburger-toggle-btn:hover {
  background-color: var(--bg-color); /* 簡單的灰色底色回饋即可 */
}

/* 側邊欄頂部 (使用者資訊) */
.sidebar-header {
  height: 60px; 
  padding: 0 20px; 
  display: flex; 
  justify-content: flex-start; 
  align-items: center;
  border-bottom: 1px solid var(--border-color); 
  background-color: var(--bg-color);
  box-sizing: border-box;
}
.user-info { background: none; border: none; display: flex; align-items: center; gap: 10px; font-weight: bold; color: var(--primary-color);}
.logout-btn-small { background: none; border: none; cursor: pointer; font-size: 18px; transition: 0.2s; }
.logout-btn-small:hover { transform: scale(1.1); }

.header-right {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1; 
}
.auth-buttons { display: flex; gap: 10px; width: 100%; }
.auth-btn { flex: 1; padding: 8px; border-radius: 6px; cursor: pointer; font-weight: bold; border: 1px solid var(--primary-color); }
.auth-btn.login { background: transparent; color: var(--primary-color); }
.auth-btn.register { background: var(--primary-color); color: white; }

/* 加入行程輸入框 */
.sidebar-section { padding: 15px 20px; border-bottom: 1px solid var(--border-color); }
.join-trip-box { display: flex; background: var(--bg-color); border-radius: 8px; border: 1px solid var(--border-color); overflow: hidden; }
.join-trip-box input { flex: 1; border: none; background: transparent; padding: 10px; outline: none; color: var(--text-color); }
.join-trip-box button { background: var(--primary-color); color: white; border: none; padding: 0 15px; cursor: pointer; }

/* 導覽按鈕 */
.sidebar-nav { padding: 15px 0; display: flex; flex-direction: column; }

.nav-item {
  padding: 15px 20px; color: var(--text-color); text-decoration: none;
  cursor: pointer; transition: background 0.2s; font-size: 16px;
  display: block; user-select: none;
}
.nav-item:hover { background-color: var(--bg-color); color: var(--primary-color); }
.nav-item.active { background-color: rgba(var(--primary-color-rgb), 0.1); color: var(--primary-color); font-weight: bold; border-left: 4px solid var(--primary-color); }

/* AI 按鈕設計 */
.ai-btn { background: linear-gradient(90deg, #fff3e0, #ffe0b2); color: #e65100; font-weight: bold; margin: 0 10px 10px 10px; border-radius: 8px; border-left: none !important;}
.ai-btn:hover { background: linear-gradient(90deg, #ffe0b2, #ffcc80); }
.ai-btn.active { background: linear-gradient(90deg, #ffcc80, #ffb74d); color: #fff; }

/* 摺疊選單 (<details>) */
.nav-details summary { list-style: none; outline: none; }
.nav-details summary::-webkit-details-marker { display: none; } /* 隱藏原生箭頭 */
.nav-details summary::after { content: ' ▼'; font-size: 12px; float: right; margin-top: 4px; color: #999; }
.nav-details[open] summary::after { content: ' ▲'; }
.details-content { background-color: var(--bg-color); padding: 5px 0; }
.details-content a { display: block; padding: 10px 20px 10px 40px; color: var(--text-secondary); cursor: pointer; font-size: 14px; }
.details-content a:hover { color: var(--primary-color); font-weight: bold; }

/* 背景遮罩 */
.sidebar-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: rgba(0, 0, 0, 0.4); z-index: 90; backdrop-filter: blur(2px);
}

/* RWD 微調 */
@media (max-width: 600px) {
  .search-bar { display: none; /* 手機版空間不夠，可考慮把搜尋移到側邊欄或用 icon 取代 */ }
  .logo-area .title { font-size: 16px; }
}

/* Navbar.vue 的 style */
.navbar {
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); /* 輕微的陰影取代生硬的邊框 */
  padding: 10px 20px;
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-area {
  color: var(--primary-color); /* Logo 用標誌性藍色 */
  font-weight: 900;
  font-size: 1.5rem;
  cursor: pointer;
}

.menu-btn {
  color: var(--text-color);
  background: transparent;
  border: none;
  font-weight: 500;
  padding: 8px 12px;
}

.menu-btn:hover {
  color: var(--primary-color);
  background-color: #f0f4ff; /* 淺藍色 hover 背景 */
  border-radius: var(--radius-md);
}
</style>