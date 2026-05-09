<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios.js'

const props = defineProps({
  activePage: String,
  isDarkMode: Boolean,
  userName: String, 
  userId: String
})

const emit = defineEmits([
  'changePage', 
  'filterLocation', 
  'filterCategory',  
  'toggleTheme',
  'selectCategory',
  'logout',
  'openLogin',
])

const router = useRouter(); 
const searchQuery = ref(''); 

const isLoggedIn = computed(() => !!props.userName)
const inviteCode = ref('')
const showJoinModal = ref(false) // 控制加入行程的彈窗

// 預設為展開狀態
const isSidebarOpen = ref(true)

// 監聽螢幕寬度，手機版自動收合
const checkWindowSize = () => {
  if (window.innerWidth <= 992) {
    isSidebarOpen.value = false
  } else {
    isSidebarOpen.value = true
  }
}

onMounted(() => {
  checkWindowSize()
  window.addEventListener('resize', checkWindowSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkWindowSize)
})

const handleJoinTrip = async () => {
  if (!inviteCode.value) return alert('請輸入邀請碼')
  if (!props.userId) {
      alert('請先登入才能加入行程！')
      showJoinModal.value = false // 關閉彈窗
      router.push({ name: 'login' })
      return
  }
  
  try {
    const res = await api.post(`/api/collab/join/${inviteCode.value}`,{
      user_id: props.userId
    })
    
    alert(`🎉 ${res.data.message}`)
    inviteCode.value = '' 
    showJoinModal.value = false // 加入成功後自動關閉彈窗
    
    router.push({ name: 'user' }) 
  } catch (error) {
    console.error(error)
    const msg = error.response?.data?.detail || '加入失敗'
    alert(`❌ ${msg}`)
  }
}
  
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

const handleLogout = () => {
  if (confirm('確定要登出嗎？')) {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('user_id')
    sessionStorage.removeItem('user_name')
    emit('logout')
    alert('已成功登出')
    if (props.activePage !== 'home') {
       emit('changePage', 'home')
    }
  }
}

const handleSearch = () => {
  if (!searchQuery.value.trim()) return;
  router.push({ 
    name: 'home', 
    query: { q: searchQuery.value } 
  });
  searchQuery.value = ''; 
};

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

// 手機版點擊選單後自動收合
const handleMenuClick = (pageName) => {
  emit('changePage', pageName)
  if (window.innerWidth <= 992) isSidebarOpen.value = false
} 

const handleFilterClick = (type, value) => {
  if (type === 'location') emit('filterLocation', value)
  if (type === 'category') emit('selectCategory', value)
  if (window.innerWidth <= 992) isSidebarOpen.value = false
}
</script>

<template>
  <div class="nav-container" :class="{ 'sidebar-collapsed': !isSidebarOpen }">

    <header class="topbar">
      <div class="topbar-left">
        <button class="hamburger-btn" @click="toggleSidebar">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
        </button>

        <div class="logo-area" @click="handleMenuClick('home')">
          <span class="icon">✈️</span>
          <span class="title">旅遊GO GO GO!</span>
        </div>
      </div>

      

      <div class="topbar-right">
        <button class="theme-btn" @click="emit('toggleTheme')" title="切換風格">
          {{ isDarkMode ? '🌙' : '☀️' }}
        </button>

        <div class="header-right">
          <template v-if="isLoggedIn">
            <button class="user-info" @click="emit('changePage', 'user')" title="查看個人資料">
              👤 {{ props.userName }}
            </button>
            
            <button class=" logout-btn-small" @click="handleLogout" title="登出">登出</button>
            
          </template>
          <template v-else>
            <div class="auth-buttons">
              <button class="auth-btn login" @click="emit('openLogin')">登入 / 註冊</button>
            </div>
          </template>
        </div>
      </div>
    </header>

    <div v-if="isSidebarOpen" class="sidebar-overlay mobile-only" @click="toggleSidebar"></div>
    
    <aside class="sidebar" :class="{'is-open' : isSidebarOpen}">
      
      <div class="sidebar-section mobile-only">
         <div class="search-bar mobile-search">
          <input v-model="searchQuery" @keyup.enter="handleSearch" placeholder="搜尋景點..." />
          <button @click="handleSearch">🔍</button>
        </div>
      </div>

      <nav class="sidebar-nav">
        <a class="nav-item" :class="{ active: activePage === 'home' }" @click="handleMenuClick('home')">
          <span class="nav-icon">🏠</span> 首頁列表
        </a>
        <a class="nav-item ai-btn" :class="{ active: activePage === 'ai_planner' }" @click="handleMenuClick('ai_planner')">
          <span class="nav-icon">✨</span> AI 行程規劃
        </a>
        <a class="nav-item" :class="{ active: activePage === 'add' }" @click="handleMenuClick('add')">
          <span class="nav-icon">📍</span> 新增景點
        </a>
        <a class="nav-item" v-if="isLoggedIn" :class="{ active: activePage === 'user' }" @click="handleMenuClick('user')">
          <span class="nav-icon">📅</span> 我的行程
        </a>
        
        <div class="divider"></div>

        <details class="nav-details" >
          <summary class="nav-item title-only">🌍 探索地點</summary>
          <div class="details-content">
            <a @click="handleFilterClick('location', '')">全部地點</a>
            <a v-for="loc in locations" :key="loc.value" @click="handleFilterClick('location', loc.value)">
              {{ loc.name }}
            </a>
          </div>
        </details>

        <div class="divider"></div>

        <details class="nav-details">
          <summary class="nav-item title-only">🏷️ 景點分類</summary>
          <div class="details-content">
            <a @click="handleFilterClick('category', '全部')">所有分類</a>
            <a v-for="cat in categories" :key="cat.value" @click="handleFilterClick('category', cat.value)">
              {{ cat.name }}
            </a>
          </div>
        </details>
      </nav>

      <div class="sidebar-section bottom-section" v-if="isLoggedIn">
        <p class="section-title">行程協作</p>
        <a class="nav-item join-btn" @click="showJoinModal = true">
          <span class="nav-icon">🤝</span> 輸入邀請碼
        </a>
      </div>

    </aside>

    <div v-if="showJoinModal" class="modal-overlay" @click.self="showJoinModal = false">
      <div class="modal-content">
        <h3>🤝 加入協作行程</h3>
        <p>請輸入好友提供的邀請碼：</p>
        <input 
          v-model="inviteCode" 
          class="modal-input" 
          placeholder="例如：A1B2C3D4" 
          @keyup.enter="handleJoinTrip" 
        />
        <div class="modal-actions">
            <button @click="handleJoinTrip" class="btn-confirm">確定加入</button>
            <button @click="showJoinModal = false" class="btn-cancel">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 頂部列樣式 (橫跨全寬) */
.topbar {
  background-color: var(--nav-bg);
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  position: fixed; 
  top: 0; left: 0; 
  width: 100%; height: 68px; 
  z-index: 200;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 20px; 
  box-sizing: border-box;
  border-bottom: 1px solid var(--border-color);
}

.topbar-left, .topbar-right {
  display: flex; align-items: center; gap: 15px;
}

.topbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 0 20px;
}

.hamburger-btn {
  background: none; border: none; cursor: pointer;
  color: var(--text-color); padding: 8px; border-radius: 8px; 
  display: flex; align-items: center; justify-content: center;
  transition: background-color 0.2s;
}
.hamburger-btn:hover { background-color: var(--input-bg); }

.logo-area { display: flex; align-items: center; gap: 8px; cursor: pointer; user-select: none; }
.logo-area .icon { font-size: 24px; }
.logo-area .title { font-size: 22px; font-weight: 900; color: var(--primary-color); letter-spacing: -0.5px;}

/* 頂部置中搜尋列 (Trip.com 風格) */
.search-bar { 
  display: flex; align-items: center; background: var(--bg-color); 
  border-radius: 24px; border: 2px solid var(--border-color);
  width: 100%; max-width: 500px;
  overflow: hidden;
  transition: border-color 0.3s;
}
.search-bar:focus-within { border-color: var(--primary-color); }
.search-bar input { flex: 1; border: none; background: transparent; padding: 10px 16px; outline: none; color: var(--text-color); font-size: 15px;}
.search-submit-btn { 
  background: var(--primary-color); color: white; border: none; 
  padding: 0 20px; height: 100%; cursor: pointer; 
  border-radius: 0 20px 20px 0;
  transition: opacity 0.2s;
}
.search-submit-btn:hover { opacity: 0.9; }

.theme-btn {
  background: none; border: 1px solid var(--border-color); border-radius: 50%;
  width: 36px; height: 36px; cursor: pointer; font-size: 16px;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-color); transition: 0.3s;
}
.theme-btn:hover { background-color: var(--bg-color); }

.header-right { display: flex; align-items: center; gap: 15px; }
.user-info { background: none; border: none; display: flex; align-items: center; gap: 8px; font-weight: 600; color: var(--text-color); cursor: pointer; }
.user-info:hover { color: var(--primary-color); }
.logout-btn-small { background: none; border: none; cursor: pointer; font-size: 14px; color: var(--text-secondary); transition: 0.2s; font-weight: bold; }
.logout-btn-small:hover { color: #e74c3c; }

.auth-btn.login { 
  background: rgba(50, 100, 255, 0.1); color: var(--primary-color); border: none; 
  padding: 8px 18px; border-radius: 20px; font-weight: bold; cursor: pointer;
  transition: all 0.3s;
}
.auth-btn.login:hover { background: var(--primary-color); color: white; }

/* ================= 側邊欄 (Trip.com 風格) ================= */
.sidebar {
  position: fixed; 
  top: 68px; /* 在 topbar 下方 */
  left: 0; 
  width: 250px; 
  height: calc(100vh - 68px);
  background-color: var(--nav-bg); 
  border-right: 1px solid var(--border-color);
  z-index: 100; 
  display: flex; flex-direction: column;
  transform: translateX(-100%); 
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
}
.sidebar.is-open { transform: translateX(0); }

/* 讓捲軸變好看 */
.sidebar::-webkit-scrollbar { width: 6px; }
.sidebar::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; }

.sidebar-nav { padding: 15px 10px; display: flex; flex-direction: column; flex: 1;}

.nav-item { 
  display: flex; align-items: center;
  padding: 12px 15px; color: var(--text-color); 
  text-decoration: none; cursor: pointer; 
  border-radius: 8px; font-size: 15px; font-weight: 500;
  margin-bottom: 4px; transition: all 0.2s; user-select: none;
}
.nav-icon { margin-right: 12px; font-size: 18px; width: 24px; text-align: center; }

.nav-item:hover { background-color: var(--input-bg); color: var(--primary-color); }
.nav-item.active { background-color: rgba(50, 100, 255, 0.08); color: var(--primary-color); font-weight: bold; }

.nav-item.title-only { font-weight: bold; color: var(--text-secondary); background: none; cursor: default; padding: 10px 15px; font-size: 13px;}
.nav-item.title-only:hover { color: var(--text-secondary); }

.divider { height: 1px; background-color: var(--border-color); margin: 15px 10px; }

/* 摺疊選單重構 */
.nav-details summary::-webkit-details-marker { display: none; } 
.details-content { display: flex; flex-direction: column; padding-left: 10px;}
.details-content a { 
  padding: 10px 15px 10px 42px; color: var(--text-color); 
  cursor: pointer; font-size: 14px; border-radius: 8px; margin-bottom: 2px;
  transition: all 0.2s;
}
.details-content a:hover { background-color: var(--input-bg); color: var(--primary-color); font-weight: 500;}

/* 底部行程加入按鈕 */
.bottom-section { padding: 20px; background-color: var(--input-bg); margin-top: auto;}
.section-title { font-size: 13px; font-weight: bold; color: var(--text-secondary); margin: 0 0 10px 0;}

.join-btn {
  background-color: var(--card-bg);
  border: 1px dashed var(--border-color);
  color: var(--primary-color);
  font-weight: bold;
  justify-content: center;
  margin-top: 10px;
}
.join-btn .nav-icon { margin-right: 8px; }
.join-btn:hover {
  background-color: rgba(50, 100, 255, 0.1);
  border-color: var(--primary-color);
}

.mobile-only { display: none; }

/* ================= Modal 彈窗樣式 ================= */
.modal-overlay {
  position: fixed; 
  top: 0; 
  left: 0; 
  width: 100vw; 
  height: 100vh;
  background: rgba(0, 0, 0, 0.6); 
  backdrop-filter: blur(4px);
  display: flex; 
  justify-content: center; 
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background-color: var(--card-bg, #ffffff); 
  color: var(--text-color, #333333);
  padding: 35px 30px; 
  border-radius: 16px;
  width: 90%; 
  max-width: 380px; 
  text-align: center;
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
  animation: fadeInDown 0.3s ease-out;
  border: 1px solid var(--border-color, #eeeeee);
}

.modal-content h3 { 
  margin: 0 0 15px 0; 
  font-size: 1.4rem; 
  font-weight: bold;
}

.modal-content p { 
  color: var(--text-secondary, #666666); 
  font-size: 14px; 
  margin-bottom: 25px;
}

.modal-input {
  width: 100%; 
  padding: 14px; 
  margin-bottom: 25px;
  border-radius: 8px; 
  border: 1px solid var(--border-color, #dddddd);
  background-color: var(--input-bg, #f9f9f9); 
  color: var(--text-color, #333333);
  box-sizing: border-box; 
  font-size: 16px; 
  text-align: center; 
  letter-spacing: 1px;
}

.modal-input:focus { 
  outline: none; 
  border-color: var(--primary-color, #3264ff); 
  box-shadow: 0 0 0 3px rgba(50, 100, 255, 0.15); 
}

.modal-actions { 
  display: flex; 
  gap: 12px; 
  justify-content: center; 
}

.btn-confirm { 
  flex: 1; 
  background-color: var(--primary-color, #3264ff); 
  color: white; 
  border: none; 
  padding: 12px; 
  border-radius: 8px; 
  cursor: pointer; 
  font-weight: bold; 
  font-size: 15px; 
  transition: all 0.2s;
}
.btn-confirm:hover { 
  transform: translateY(-2px); 
  box-shadow: 0 4px 10px rgba(50, 100, 255, 0.3); 
}

.btn-cancel { 
  flex: 1; 
  background-color: var(--input-bg, #f1f1f1); 
  color: var(--text-secondary, #666666); 
  border: 1px solid var(--border-color, #dddddd); 
  padding: 12px; 
  border-radius: 8px; 
  cursor: pointer; 
  font-weight: bold; 
  font-size: 15px; 
  transition: all 0.2s;
}
.btn-cancel:hover { 
  background-color: #e2e2e2; 
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* RWD 響應式設計 (平板/手機) */
@media (max-width: 992px) {
  .desktop-only { display: none; }
  .mobile-only { display: block; }
  .topbar { padding: 0 15px; }
  
  .sidebar { top: 0; height: 100vh; width: 280px; box-shadow: 2px 0 10px rgba(0,0,0,0.1); z-index: 201;}
  .sidebar-overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background-color: rgba(0, 0, 0, 0.5); z-index: 200; backdrop-filter: blur(2px);
  }
  
  .mobile-search { margin-top: 20px; border-radius: 8px;}
  .mobile-search input { padding: 12px;}
  .mobile-search button { background: none; color: var(--text-secondary); }
}
</style>