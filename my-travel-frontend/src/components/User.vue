
<script setup>
//使用者個人頁面，包含個人資料編輯與行程管理功能

// --- 匯入 ---
import { ref, reactive, watch, computed } from 'vue';
import api from '../api/axios.js'; // 用封裝好的 api
import draggable from 'vuedraggable';
import rawCountries from '../assets/countries_number.json'; 

// --- 資料預處理 ---
const countryCodes = rawCountries.map(item => {
    const match = item.name.match(/\((.+?)\)/);
    return {
        label: item.name, 
        code: match ? match[1] : '' 
    };
}).filter(item => item.code);

// 定義事件與接收 Props
const emit = defineEmits(['changePage'])
const props = defineProps({
  user: Object
})

// --- 狀態變數：使用者 ---
const localUser = ref(null);    
const loading = ref(true);
const error = ref(null);
const isEditing = ref(false);

// --- 狀態變數：行程 ---
const itineraries = ref([]);
const activeItinerary = ref(null);
const isCreatingItinerary = ref(false); 

// 紀錄目前使用者 ID
const currentUserId = computed(() => props.user ? props.user.id : null);

// --- 表單資料 ---
const formData = reactive({
  name: '',
  phonePrefix: '+886', 
  phoneNumber: '',     
  birthday: '',
  likes: {}
});

// 新行程表單
const newItineraryForm = reactive({
    title: '',
    budget: 0,
    travel_time: '',
    lodging: '',
    transport: ''
});

// --- 方法：使用者資料 ---
const fetchUser = async () => {
  if (!currentUserId.value) {
    error.value = "您尚未登入，請先登入！";
    return;
  }

  try {
    loading.value = true;
    error.value = null;
    
    // 2. 抓取使用者資料
    const response = await api.get(`/api/users/${currentUserId.value}`);
    localUser.value = response.data;

    // 3. 抓取行程列表
    await fetchItineraries();

  } catch (err) {
    console.error(err);
    error.value = "無法取得資料，請確認後端是否啟動。";
    if (err.response && err.response.status === 401) {
        localStorage.clear();
        alert("登入已過期，請重新登入");
        emit('changePage', 'login'); 
    }
  } finally {
    loading.value = false;
  }
};

// --- 方法：行程管理 ---
const fetchItineraries = async () => {
    try {
        // 1. 抓取使用者的行程列表
        const res = await api.get(`/api/itineraries/user/${currentUserId.value}`);
        itineraries.value = res.data;
        
        // 如果目前有選中的行程，重新整理它的資料
        if (activeItinerary.value) {
            const found = itineraries.value.find(i => i.id === activeItinerary.value.id);
            if (found) {
                // 這裡要做一個深拷貝或者確保 spots 是按照 day_order 排序
                // 後端 API 應該已經排好了
                activeItinerary.value = found;
            } else {
                activeItinerary.value = null; 
            }
        }
    } catch (e) {
        console.error("抓取行程失敗", e);
    }
};

// 建立新行程
const createItinerary = async () => {
    if (!newItineraryForm.title) return alert("請輸入行程名稱");
    
    try {
        const payload = {
            ...newItineraryForm,
            owner_user_id: currentUserId.value,
            spot_ids: [] // 確保後端 schema 有這個欄位
        };
        await api.post(`/api/itineraries/`, payload);
        
        alert("行程建立成功！");
        isCreatingItinerary.value = false;
        Object.assign(newItineraryForm, { title: '', budget: 0, travel_time: '', lodging: '', transport: '' });
        await fetchItineraries();
    } catch (e) {
        alert("建立失敗：" + (e.response?.data?.detail || e.message));
    }
};

// 刪除行程
const deleteItinerary = async (id) => {
    if (!confirm("確定要刪除此行程嗎？(無法復原)")) return;
    try {
        await api.delete(`/api/itineraries/${id}`);
        await fetchItineraries();
    } catch (e) {
        alert("刪除失敗");
    }
};

// 從行程中移除景點
const deleteSpotFromItinerary = async (itemId) => {
    if (!confirm("確定要從行程移除此景點嗎？")) return;
    try {
        await api.delete(`/api/itineraries/item/${itemId}`);
        await fetchItineraries(); 
    } catch (e) {
        alert("移除失敗");
    }
};

// 選擇行程
const selectItinerary = (itin) => {
    activeItinerary.value = itin;
};

// 拖曳結束後，更新排序到後端
const onDragEnd = async () => {
    if (!activeItinerary.value) return;
    
    // 準備 payload：只傳送 item_id 和 new_order
    const payload = activeItinerary.value.spots.map((item, index) => ({
        item_id: item.id,   // 這是關聯表 (itinerary_spots) 的 ID
        new_order: index    // 新的順序
    }));

    try {
        await api.post(`/api/itineraries/${activeItinerary.value.id}/reorder`, payload);
        console.log("排序更新成功");
    } catch (e) {
        console.error("排序更新失敗", e);
    }
};

const getImageUrl = (id) => `https://picsum.photos/seed/${id}/200/150`; 

// --- 監聽使用者變化 ---
watch(() => props.user, (newVal) => {
  if(newVal && newVal.id) {
    fetchUser();
  } else {
    localUser.value = null;
    itineraries.value = [];
    loading.value = false;
  } 
}, { immediate: true });

// --- 編輯個人資料邏輯 ---
const startEditing = () => {
  if (!localUser.value) {
    console.error("無法編輯，使用者尚未載入");
    return;
  }
  formData.name = localUser.value.name;
  
  const fullPhone = localUser.value.phone || '';
  const foundCode = countryCodes.find(c => fullPhone.startsWith(c.code));
  
  if (foundCode) {
    formData.phonePrefix = foundCode.code;
    formData.phoneNumber = fullPhone.replace(foundCode.code, '');
  } else {
    formData.phonePrefix = '+886';
    formData.phoneNumber = fullPhone;
  }

  if (localUser.value.birthday) {
    formData.birthday = localUser.value.birthday.split('T')[0];
  } else {
    formData.birthday = '';
  }
  
  // 處理 likes (JSON)
  formData.likes = localUser.value.likes ? JSON.parse(JSON.stringify(localUser.value.likes)) : {};
  isEditing.value = true;
};

// 取消編輯
const cancelEdit = () => { isEditing.value = false; };

// 儲存使用者資料
const saveUser = async () => {
  try {
    const fullPhone = `${formData.phonePrefix}${formData.phoneNumber}`;
    const payload = {
      name: formData.name,
      phone: fullPhone, 
      birthday: formData.birthday ? new Date(formData.birthday).toISOString() : null,
      likes: formData.likes
    };
    const response = await api.put(`/api/users/${currentUserId.value}`, payload);
    localUser.value = response.data;
    isEditing.value = false;
    alert("更新成功！");
  } catch (err) {
    console.error(err);
    alert("更新失敗：" + (err.response?.data?.detail || err.message));
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未設定';
  return new Date(dateString).toLocaleDateString();
};

// 複製邀請碼到剪貼簿
const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    alert(`已複製邀請碼：${code} \n趕快傳給朋友加入協作吧！`)
  }).catch(() => {
    alert('複製失敗，請手動複製')
  })
}
</script>

<template>
  <div class="user-page-container">
    
    <div v-if="loading" class="loading">資料載入中...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="!loading && !localUser && !error" class="error">請先登入。</div>

    <div v-if="!loading && localUser" class="grid-layout">
        
        <div class="profile-section">
            <div class="profile-card">
                <h2>👤 個人資料</h2>
                <div v-if="!isEditing">
                    <div class="info-group"><label>Email：</label><span>{{ localUser.email }}</span></div>
                    <div class="info-group"><label>姓名：</label><span>{{ localUser.name || '未設定' }}</span></div>
                    <div class="info-group"><label>電話：</label><span>{{ localUser.phone || '未設定' }}</span></div>
                    <div class="info-group"><label>生日：</label><span>{{ formatDate(localUser.birthday) }}</span></div>
                    
                    <div class="info-group">
                        <label>喜好：</label>
                        <div class="tags">
                            <span v-for="(value, key) in localUser.likes" :key="key" class="tag">{{ key }}: {{ value }}</span>
                        </div>
                    </div>
                    <button @click="startEditing" class="btn-primary">編輯資料</button>
                </div>

                <div v-else class="edit-form">
                    <div class="form-group"><label>姓名</label><input v-model="formData.name" type="text" /></div>
                    <div class="form-group">
                        <label>電話</label>
                        <div class="phone-input-group">
                            <select v-model="formData.phonePrefix" class="phone-select">
                                <option v-for="c in countryCodes" :key="c.code" :value="c.code">
                                    {{ c.label }}
                                </option>
                            </select>
                            <input v-model="formData.phoneNumber" type="text" placeholder="請輸入號碼" class="phone-input" />
                        </div>
                    </div>
                    <div class="form-group"><label>生日</label><input v-model="formData.birthday" type="date" /></div>
                    <div class="form-group"><label>喜好 (Food)</label><input v-model="formData.likes.food" type="text" /></div>
                    
                    <div class="button-group">
                        <button @click="saveUser" class="btn-save">儲存</button>
                        <button @click="cancelEdit" class="btn-cancel">取消</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="itinerary-section">
            
            <div class="itin-header">
                <h2>🗓️ 我的行程 ({{ itineraries.length }})</h2>
                <button @click="isCreatingItinerary = !isCreatingItinerary" class="btn-add-itin">
                    {{ isCreatingItinerary ? '取消新增' : '+ 建立新行程' }}
                </button>
            </div>

            <div v-if="isCreatingItinerary" class="card create-itin-card">
                <h3>✨ 規劃新的旅程</h3>
                <div class="form-grid">
                    <div><label>行程名稱 *</label><input v-model="newItineraryForm.title" placeholder="例如：東京五日遊" /></div>
                    <div><label>預算 (TWD)</label><input type="number" v-model="newItineraryForm.budget" /></div>
                    <div><label>預計時間</label><input v-model="newItineraryForm.travel_time" placeholder="例如：2023/12/25" /></div>
                    <div><label>住宿安排</label><input v-model="newItineraryForm.lodging" /></div>
                    <div><label>交通方式</label><input v-model="newItineraryForm.transport" /></div>
                </div>
                <button @click="createItinerary" class="btn-submit-itin">建立行程</button>
            </div>

            <div class="itin-list">
                <div v-for="itin in itineraries" :key="itin.id" 
                     class="itin-card" 
                     :class="{ active: activeItinerary && activeItinerary.id === itin.id }"
                     @click="selectItinerary(itin)">
                    <div class="itin-info">
                        <h4>{{ itin.title }}</h4>
                        <span class="badge">{{ itin.spots ? itin.spots.length : 0 }} 個景點</span>
                        <div class="invite-code-display" @click.stop>
                            🔑 邀請碼：<span class="code-text">{{ itin.code }}</span>
                            <button class="btn-copy" @click="copyCode(itin.code)">複製</button>
                        </div>
                    </div>
                    <div class="members-display">
                        <div class="owner-tag" v-if="itin.owner">
                            👑 {{ itin.owner.name }} (房主)
                        </div>
        
                    <div v-if="itin.collaborators && itin.collaborators.length > 0" class="collab-list">
                        <span v-for="user in itin.collaborators" :key="user.id" class="collab-tag">
                            👤 {{ user.name }}
                        </span>
                    </div>
                    </div>
                    <button @click.stop="deleteItinerary(itin.id)" class="btn-delete-itin">🗑️</button>
                </div>
                <div v-if="itineraries.length === 0" class="empty-hint">尚未建立行程</div>
            </div>

            <hr class="divider">

            <div v-if="activeItinerary" class="itin-detail">
                <h3>
                    📍 {{ activeItinerary.title }} - 景點規劃
                    <small style="font-size:0.9rem; color:var(--text-secondary)"> (預算: ${{ activeItinerary.budget }})</small>
                </h3>
                
                <draggable 
                    v-model="activeItinerary.spots" 
                    item-key="id" 
                    @end="onDragEnd"
                    class="drag-area"
                >
                    <template #item="{ element }">
                        <div class="spot-item">
                            <div class="drag-handle">☰</div>
                            <img :src="getImageUrl(element.spot.id)" class="spot-thumb">
                            <div class="spot-content">
                                <strong>{{ element.spot.name }}</strong>
                                <p>{{ element.spot.location }} | {{ element.spot.category }}</p>
                            </div>
                            <button @click="deleteSpotFromItinerary(element.id)" class="btn-remove-spot">✕</button>
                        </div>
                    </template>
                </draggable>

                <div v-if="(!activeItinerary.spots || activeItinerary.spots.length === 0)" class="empty-spots">
                    此行程還沒有景點，請去首頁加入！
                </div>
            </div>
            <div v-else class="no-selection">
                請點選上方行程以查看詳情
            </div>

        </div>
    </div>
  </div>
</template>

<style scoped>
/* 樣式保持不變，直接沿用您原本的 CSS */
.user-page-container { max-width: 1400px; width: 95%; margin: 0 auto; padding: 30px 20px; color: var(--text-color); }
.grid-layout { display: grid; grid-template-columns: 280px 1fr; gap: 30px; align-items: start; }
@media(max-width: 768px) { .grid-layout { grid-template-columns: 1fr; } }
.profile-card, .card, .itin-card, .create-itin-card { background: var(--card-bg); padding: 25px; border-radius: 16px; border: 1px solid var(--border-color); box-shadow: 0 4px 10px var(--shadow-color); }
.info-group, .form-group { margin-bottom: 15px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }
label { display: block; font-weight: bold; margin-bottom: 8px; color: var(--text-secondary); }
span { color: var(--text-color); font-size: 1.1rem; }
input, select { width: 100%; padding: 10px; border: 1px solid var(--input-border); border-radius: 6px; background-color: var(--input-bg); color: var(--text-color); transition: all 0.3s; box-sizing: border-box; }
input:focus, select:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1); }
.phone-input-group { display: flex; gap: 10px; }
.phone-select { width: 35%; flex-shrink: 0; }
.phone-input { flex-grow: 1; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { background-color: var(--input-bg); color: var(--primary-color); padding: 5px 12px; border-radius: 20px; font-size: 0.9rem; border: 1px solid var(--border-color); }
.btn-primary, .btn-save, .btn-cancel, .btn-submit-itin { width: 100%; padding: 12px; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; margin-top: 10px; }
.btn-primary { background: var(--primary-color); color: white; }
.btn-save { background: #2ecc71; color: white; }
.btn-cancel { background: #e74c3c; color: white; }
.button-group { display: flex; gap: 10px; }
.itin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.btn-add-itin { background: var(--primary-color); color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; }
.btn-submit-itin { margin-top: 20px; }
.itin-list { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; overflow-x: auto; padding-bottom: 10px; }
.itin-card { width: 100%; box-sizing: border-box; padding: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: var(--input-bg); transition: all 0.2s; }
@media (max-width: 600px) {
  .itin-list {
    grid-template-columns: 1fr;
  }
}
.itin-card:hover { transform: translateY(-3px); }
.itin-card.active { border-color: var(--primary-color); background: rgba(76, 175, 80, 0.1); }
.itin-info h4 { margin: 0 0 5px 0; color: var(--text-color); }
.badge { background: #666; color: white; font-size: 0.8rem; padding: 2px 6px; border-radius: 4px; }
.btn-delete-itin { background: none; border: none; cursor: pointer; font-size: 1.2rem; color: #aaa; }
.btn-delete-itin:hover { color: #e74c3c; }
.create-itin-card { margin-bottom: 20px; background: var(--input-bg); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.drag-area { margin-top: 15px; }
.spot-item { display: flex; align-items: center; background: var(--card-bg); border: 1px solid var(--border-color); padding: 10px; margin-bottom: 10px; border-radius: 8px; transition: background 0.2s; }
.spot-item:hover { background: var(--input-bg); }
.drag-handle { cursor: grab; padding: 0 10px; font-size: 1.5rem; color: #888; }
.spot-thumb { width: 60px; height: 45px; object-fit: cover; border-radius: 4px; margin-right: 15px; }
.spot-content { flex: 1; }
.spot-content strong { color: var(--text-color); }
.spot-content p { margin: 3px 0 0; font-size: 0.9rem; color: var(--text-secondary); }
.btn-remove-spot { background: none; border: none; color: #aaa; cursor: pointer; font-size: 1.2rem; }
.btn-remove-spot:hover { color: #e74c3c; }
.divider { border: 0; height: 1px; background: var(--border-color); margin: 20px 0; }
.empty-hint, .no-selection, .empty-spots { text-align: center; color: var(--text-secondary); padding: 30px; border: 2px dashed var(--border-color); border-radius: 12px; }
.loading, .error { text-align: center; margin-top: 50px; font-size: 1.2rem; color: var(--text-secondary); }
.error { color: #e74c3c; }
.invite-code-display {
    margin-top: 8px;
    font-size: 0.9rem;
    color: #666;
    background: rgba(0,0,0,0.03);
    padding: 4px 8px;
    border-radius: 4px;
    display: inline-flex; /* 讓它變成一行 */
    align-items: center;
    gap: 5px;
}

.code-text {
    font-weight: bold;
    color: var(--primary-color);
    letter-spacing: 1px;
    user-select: all; /* 讓使用者點一下就能全選文字 */
}

.btn-copy {
    background: none;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    padding: 2px 6px;
    color: #666;
    transition: all 0.2s;
}

.btn-copy:hover {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}
.members-display {
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    align-items: center;
}

.owner-tag {
    font-size: 0.85rem;
    background-color: #fff8e1; /* 淡黃色 */
    color: #f57c00;
    padding: 2px 8px;
    border-radius: 10px;
    border: 1px solid #ffe0b2;
}

.collab-list {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}

.collab-tag {
    font-size: 0.85rem;
    background-color: #e3f2fd; /* 淡藍色 */
    color: #1976d2;
    padding: 2px 8px;
    border-radius: 10px;
    border: 1px solid #bbdefb;
}
</style>