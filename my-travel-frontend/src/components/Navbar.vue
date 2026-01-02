<script setup>
import { computed, ref } from 'vue'


const props = defineProps({
  activePage: String,
  isDarkMode: Boolean,
  userName: String //接收來自 App.vue 的使用者名稱
})

const emit = defineEmits([
  'changePage', 
  'filterLocation', 
  'filterCategory', 
  'filterAccommodation', 
  'toggleTheme',
  'selectCategory',
  'logout'
])

// --- 狀態變數 ---
const isLoggedIn = computed(() => !!props.userName)
const userName = ref('')

// --- 下拉選單資料 ---
const locations = [
  { name: '亞洲', value: 'Asia' },
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

const accommodations = [
  { name: '🏨 飯店', value: '飯店' },
  { name: '🏩 民宿', value: '民宿' },
  { name: '🏕️ 露營', value: '露營' },
  { name: '🛏️ 青年旅館', value: '青年旅館' },
  { name: '🏠 公寓式住宿', value: '公寓式住宿' }
]

// --- 方法 ---

// 檢查登入狀態
const checkLoginStatus = () => {
  const token = localStorage.getItem('token')
  const name = localStorage.getItem('userName')
  
  if (token && name) {
    isLoggedIn.value = true
    userName.value = name
  } else {
    isLoggedIn.value = false
    userName.value = ''
  }
}

// 登出功能
const handleLogout = () => {
  if (confirm('確定要登出嗎？')) {
    // 1. 清除 localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // 2. 跳轉回登入頁或首頁
    alert('已成功登出')
    window.location.href = '/'
  }
}
</script>

<template>
  <nav class="navbar">
    <div class="container">
      
      <div 
        class="logo-area" 
        @click="emit('changePage', 'home'); emit('filterLocation', ''); emit('filterCategory', '全部'); emit('filterAccommodation', '')"
      >
        <span class="icon">✈️</span>
        <span class="title">旅遊GO GO GO!</span>
      </div>

      <div class="menu-area">
        <button 
          class="menu-btn" 
          :class="{ active: activePage === 'home' }"
          @click="emit('changePage', 'home')"
        >
          🏠 首頁列表
        </button>

        <div class="dropdown">
          <button class="menu-btn dropdown-trigger">
            🌍 探索地點 ▼
          </button>
          <div class="dropdown-content">
            <a @click.stop="emit('changePage', 'home'); emit('filterLocation', '')">全部地點</a>
            <a 
              v-for="loc in locations" 
              :key="loc.value"
              @click.stop="emit('changePage', 'home'); emit('filterLocation', loc.value)"
            >
              {{ loc.name }}
            </a>
          </div>
        </div>

        <div class="dropdown">
          <button class="menu-btn dropdown-trigger">
            🏷️ 景點分類 ▼
          </button>
          <div class="dropdown-content">
            <a @click.stop="emit('changePage', 'home'); emit('selectCategory', '全部')">所有分類</a>
            <a 
              v-for="cat in categories" 
              :key="cat.value"
              @click.stop="emit('changePage', 'home'); emit('selectCategory', cat.value)"
            >
              {{ cat.name }}
            </a>
          </div>
        </div>

        <div class="dropdown">
          <button class="menu-btn dropdown-trigger">
            🛏️ 住宿類型 ▼
          </button>
          <div class="dropdown-content">
             <a @click.stop="emit('changePage', 'home'); emit('filterAccommodation', '')">全部住宿</a>
             <a 
               v-for="acc in accommodations" 
               :key="acc.value"
               @click.stop="emit('changePage', 'home'); emit('filterAccommodation', acc.value)"
             >
               {{ acc.name }}
             </a>
          </div>
        </div>
        <button 
          class="menu-btn ai-btn" 
          :class="{ active: activePage === 'ai_planner' }"
          @click="emit('changePage', 'ai_planner')"
          >
          AI 行程規劃/推薦
        </button>
      </div>

      <div class="action-area">

        <button class="theme-btn" @click="emit('toggleTheme')" title="切換風格">
          {{ isDarkMode ? '🌙' : '☀️' }}
        </button>

        <button 
          class="add-btn" 
          @click="emit('changePage', 'add')"
        >
           新增景點
        </button>

        <div class="user-auth">
          
          <template v-if="!isLoggedIn">
            <button 
              class="text-btn" 
              :class="{ active: activePage === 'register' }"
              @click="emit('changePage', 'register')"
            >
              註冊
            </button>
            <span class="divider">|</span>
            <button 
              class="text-btn" 
              :class="{ active: activePage === 'login' }"
              @click="emit('changePage', 'login')"
            >
              登入
            </button>
          </template>

          <template v-else>
            <button 
              class="text-btn user-name-btn" 
              :class="{ active: activePage === 'user' }"
              @click="emit('changePage', 'user')"
              title="查看個人資料"
            >
              👤 {{props.userName }}
            </button>
            <span class="divider">|</span>
            <button class="text-btn logout-btn" @click="handleLogout">
              登出
            </button>
          </template>

        </div>
      </div>

    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background-color: var(--nav-bg);
  box-shadow: 0 2px 10px var(--shadow-color);
  position: fixed; top: 0; left: 0; width: 100%; height: 64px; z-index: 1000;
  transition: background-color 0.3s;
}
.nav-categories {
    display: flex;
    gap: 15px;
}
.container {
  max-width: 100%; width: 100%; margin: 0; padding: 0 40px; height: 100%;
  display: flex; justify-content: space-between; align-items: center; box-sizing: border-box;
}
.logo-area { display: flex; align-items: center; gap: 8px; cursor: pointer; user-select: none; }
.logo-area:hover { opacity: 0.8; }
.icon { font-size: 24px; }
.title { font-size: 20px; font-weight: bold; color: var(--text-color); white-space: nowrap; }

.menu-area { display: flex; gap: 20px; }
@media (max-width: 768px) { .menu-area { display: none; } }

.menu-btn {
  background: none; border: none; font-size: 16px; color: var(--text-secondary);
  cursor: pointer; padding: 8px 12px; border-radius: 6px; transition: all 0.2s; white-space: nowrap;
}
.menu-btn:hover { background-color: var(--bg-color); color: var(--primary-color); }
.menu-btn.active { background-color: var(--bg-color); color: var(--primary-color); font-weight: bold; }

.dropdown { position: relative; display: inline-block; }
.dropdown-content {
  display: none; position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
  background-color: var(--card-bg); min-width: 140px; box-shadow: 0 8px 16px var(--shadow-color);
  border-radius: 8px; padding: 8px 0; border: 1px solid var(--border-color);
}
.dropdown:hover .dropdown-content { display: block; }
.dropdown-content a {
  color: var(--text-color); padding: 10px 16px; text-decoration: none;
  display: block; cursor: pointer; text-align: center; white-space: nowrap;
}
.dropdown-content a:hover { background-color: var(--bg-color); color: var(--primary-color); }

.action-area { display: flex; align-items: center; gap: 15px; }

.theme-btn {
  background: none; border: 1px solid var(--border-color); border-radius: 50%;
  width: 36px; height: 36px; cursor: pointer; font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.3s; color: var(--text-color);
}
.theme-btn:hover { background-color: var(--bg-color); transform: rotate(15deg); }

.add-btn {
  background-color: var(--primary-color); color: white; border: none; padding: 8px 20px;
  border-radius: 20px; font-weight: bold; cursor: pointer; transition: opacity 0.2s; white-space: nowrap;
}
.add-btn:hover { opacity: 0.9; transform: translateY(-2px); }

/* --- Auth 區塊樣式 --- */
.user-auth {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-secondary);
  font-size: 14px;
}

.text-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  padding: 5px 8px; /* 增加一點點點擊範圍 */
  transition: color 0.2s;
  border-radius: 4px;
}

.text-btn:hover {
  color: var(--primary-color);
  font-weight: bold;
}

/* 當下頁面是 active 時的樣式 */
.text-btn.active {
  color: var(--primary-color);
  font-weight: bold;
}

.divider {
  color: var(--border-color);
}

.user-name-btn {
  color: var(--primary-color);
  font-weight: 600;
}

.logout-btn:hover {
  color: #e74c3c; /* 登出按鈕 hover 變紅色，表示警告 */
}
/* AI 按鈕特殊樣式 */
.ai-btn {
  background: linear-gradient(45deg, #FF6B6B, #FFD93D); /* 漸層色 */
  color: white !important; /* 強制白字 */
  font-weight: bold;
  border-radius: 20px; /* 圓角大一點 */
  padding: 8px 16px;
  box-shadow: 0 4px 10px rgba(255, 107, 107, 0.3);
  transition: transform 0.2s, box-shadow 0.2s;
}

.ai-btn:hover {
  transform: translateY(-2px) scale(1.05); /* 浮起來 */
  box-shadow: 0 6px 15px rgba(255, 107, 107, 0.5);
  background: linear-gradient(45deg, #FF8E53, #FF6B6B);
}

/* 當被選中時的樣式 */
.ai-btn.active {
  box-shadow: inset 0 2px 5px rgba(0,0,0,0.2);
  transform: translateY(0);
}
</style>