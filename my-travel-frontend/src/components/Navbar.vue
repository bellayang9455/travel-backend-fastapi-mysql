<script setup>
defineProps({
  activePage: String
})

const emit = defineEmits(['changePage', 'filterLocation'])

const locations = [
  { name: '亞洲', value: 'Asia' },
  { name: '歐洲', value: 'Europe' },
  { name: '美洲', value: 'Americas' },
  { name: '大洋洲', value: 'Oceania' },
  { name: '台灣', value: 'Taiwan' }
]
</script>

<template>
  <nav class="navbar">
    <div class="container">
      
      <!-- 左側 Logo -->
      <div 
        class="logo-area" 
        @click="emit('changePage', 'home'); emit('filterLocation', '')"
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

        <!-- 下拉選單 -->
        <div class="dropdown">
          <button class="menu-btn dropdown-trigger">
            🌍 探索地點 ▼
          </button>
          
          <div class="dropdown-content">
            <a 
              v-for="loc in locations" 
              :key="loc.value"
              @click.stop="emit('changePage', 'home'); emit('filterLocation', loc.value)"
            >
              {{ loc.name }}
            </a>
          </div>
          <div class="">

          </div>
        </div>
      </div>

      <!-- 右側動作按鈕 -->
      <div class="action-area">
        <button 
          class="add-btn" 
          @click="emit('changePage', 'add')"
        >
          ➕ 新增景點
        </button>
      </div>

    </div>
  </nav>
</template>

<style scoped>
/* 1. 導覽列外框 */
.navbar {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1); /* 底部陰影 */
  
  /* ⭐ 關鍵修改：使用 fixed 讓它永遠浮在最上面 ⭐ */
  position: fixed; 
  top: 0;
  left: 0;
  
  /* ⭐ 關鍵修改：寬度 100% 強制填滿螢幕 ⭐ */
  width: 100%;
  
  height: 64px;
  z-index: 1000; /* 層級設高一點，確保蓋過內容 */
}

/* 2. 內容容器 */
.container {
  /* ⭐ 關鍵修改：不限制最大寬度，讓它撐開 ⭐ */
  max-width: 100%;
  width: 100%;
  
  margin: 0; /* 移除 auto，因為我們已經滿版了 */
  padding: 0 40px; /* 左右留點空隙比較好看 */
  height: 100%;
  
  display: flex;
  justify-content: space-between; /* 左右撐開 */
  align-items: center; /* 垂直置中 */
  box-sizing: border-box; /* 確保 padding 不會把寬度撐破 */
}

/* 3. Logo 區域 */
.logo-area {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.logo-area:hover {
  opacity: 0.8;
}

.icon {
  font-size: 24px;
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  /* 防止手機版文字換行 */
  white-space: nowrap; 
}

/* 4. 中間選單按鈕 */
.menu-area {
  display: flex;
  gap: 20px;
}

/* 手機版隱藏中間選單，避免擠爆 (可選) */
@media (max-width: 768px) {
  .menu-area {
    display: none;
  }
}

.menu-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
}

.menu-btn:hover {
  background-color: #f5f5f5;
  color: #007bff;
}

.menu-btn.active {
  background-color: #e6f0ff;
  color: #007bff;
  font-weight: bold;
}

/* 5. 下拉選單 (Dropdown) */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-content {
  display: none;
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: white;
  min-width: 120px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
  border-radius: 8px;
  padding: 8px 0;
  border: 1px solid #eee;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-content a {
  color: #333;
  padding: 10px 16px;
  text-decoration: none;
  display: block;
  cursor: pointer;
  text-align: center;
  white-space: nowrap;
}

.dropdown-content a:hover {
  background-color: #f0f7ff;
  color: #007bff;
}

/* 6. 右邊新增按鈕 */
.add-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.add-btn:hover {
  background-color: #218838;
  transform: translateY(-2px);
}
</style>