<script setup>
defineProps({
  activePage: String,
  isDarkMode: Boolean
})

const emit = defineEmits(['changePage', 'filterLocation', 'filterCategory', 'filterAccommodation', 'toggleTheme'])

const locations = [
  { name: '亞洲', value: 'Asia' },
  { name: '歐洲', value: 'Europe' },
  { name: '美洲', value: 'Americas' },
  { name: '大洋洲', value: 'Oceania' },
  { name: '台灣', value: 'Taiwan' }
]

const categories = [
  { name: '🏞️ 自然生態', value: '自然' },
  { name: '🏯 歷史人文', value: '文化' },
  { name: '🍜 在地美食', value: '美食' },
  { name: '🎡 休閒娛樂', value: '娛樂' },
  { name: '🛍️ 購物商圈', value: '購物' },
  { name: '📸 網美打卡', value: '打卡' },
  { name: '✨ 其他', value: '其他' }
]

const accommodations = [
  { name: '🏨 飯店', value: '飯店' },
  { name: '🏩 民宿', value: '民宿' },
  { name: '🏕️ 露營', value: '露營' },
  { name: '🛏️ 青年旅館', value: '青年旅館' },
  { name: '🏠 公寓式住宿', value: '公寓式住宿' }
]
</script>

<template>
  <nav class="navbar">
    <div class="container">
      
      <!-- 左側 Logo -->
      <div 
        class="logo-area" 
        @click="emit('changePage', 'home'); emit('filterLocation', ''); emit('filterCategory', ''); emit('filterAccommodation', '')"
      >
        <span class="icon">✈️</span>
        <span class="title">旅遊日記</span>
      </div>

      <!-- 中間選單 -->
      <div class="menu-area">
        <button 
          class="menu-btn" 
          :class="{ active: activePage === 'home' }"
          @click="emit('changePage', 'home')"
        >
          🏠 首頁列表
        </button>

        <!-- 地點下拉選單 -->
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

        <!-- 分類下拉選單 -->
        <div class="dropdown">
          <button class="menu-btn dropdown-trigger">
            🏷️ 景點分類 ▼
          </button>
          <div class="dropdown-content">
            <a @click.stop="emit('changePage', 'home'); emit('filterCategory', '')">全部顯示</a>
            <a 
              v-for="cat in categories" 
              :key="cat.value"
              @click.stop="emit('changePage', 'home'); emit('filterCategory', cat.value)"
            >
              {{ cat.name }}
            </a>
          </div>
        </div>

        <!-- 住宿下拉選單 -->
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
      </div>

      <!-- 右側動作按鈕 -->
      <div class="action-area">
        
        <!-- 風格切換 -->
        <button class="theme-btn" @click="emit('toggleTheme')" title="切換風格">
          {{ isDarkMode ? '🌙' : '☀️' }}
        </button>

        <button 
          class="add-btn" 
          @click="emit('changePage', 'add')"
        >
          ➕ 新增景點
        </button>

        <!-- ⭐ 修改：註冊/登入區塊 -->
        <div class="user-auth">
          <!-- 點擊註冊，切換到 register 頁面 -->
          <button class="text-btn" @click="emit('changePage', 'register')">
            註冊
          </button>
          <span class="divider">|</span>
          <button class="text-btn">
            登入
          </button>
        </div>
      </div>

    </div>
  </nav>
</template>

<style scoped>
/* (保留原本的所有 CSS，只新增 user-auth 相關的) */
.navbar {
  background-color: var(--nav-bg);
  box-shadow: 0 2px 10px var(--shadow-color);
  position: fixed; top: 0; left: 0; width: 100%; height: 64px; z-index: 1000;
  transition: background-color 0.3s;
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

/* ⭐ 新增：使用者登入/註冊區塊樣式 */
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
  padding: 5px;
  transition: color 0.2s;
}

.text-btn:hover {
  color: var(--primary-color);
  font-weight: bold;
}

.divider {
  color: var(--border-color);
}
</style>