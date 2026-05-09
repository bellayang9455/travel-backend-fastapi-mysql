<script setup>
// 使用者個人頁面，包含個人資料編輯、行程規劃(含時間)與記帳功能
import { ref, reactive, watch, computed } from 'vue';
import api from '../api/axios.js'; 
import draggable from 'vuedraggable';
import rawCountries from '../assets/countries_number.json';
import ExpenseSection from '../components/ExpenseSection.vue'; 

// 資料預處理
const countryCodes = rawCountries.map(item => {
    const match = item.name.match(/\((.+?)\)/);
    return {
        label: item.name, 
        code: match ? match[1] : '' 
    };
}).filter(item => item.code);

const emit = defineEmits(['changePage'])
const props = defineProps({
  user: Object
})

const activeTab = ref('itinerary'); 
const itinSortBy = ref('newest');

const localUser = ref(null);    
const loading = ref(true);
const error = ref(null);
const isEditing = ref(false);

const itineraries = ref([]);
const activeItinerary = ref(null);
const isCreatingItinerary = ref(false); 

const currentUserId = computed(() => props.user ? props.user.id : null);

// 計算排序後的行程列表 (左側/上方 行程卡片用)
const sortedItineraries = computed(() => {
    let list = [...itineraries.value];
    
    if (itinSortBy.value === 'newest') {
        return list.sort((a, b) => b.id - a.id);
    } else if (itinSortBy.value === 'oldest') {
        return list.sort((a, b) => a.id - b.id);
    } else if (itinSortBy.value === 'travel_time') {
        return list.sort((a, b) => {
            const timeA = a.travel_time ? new Date(a.travel_time).getTime() : Infinity;
            const timeB = b.travel_time ? new Date(b.travel_time).getTime() : Infinity;
            return timeA - timeB;
        });
    }
    return list;
});

const formData = reactive({
  name: '',
  phonePrefix: '+886', 
  phoneNumber: '',     
  birthday: '',
  likes: {}
});

const newItineraryForm = reactive({
    title: '',
    budget: 0,
    travel_time: '',
    transport: ''
});

const allMembers = computed(() => {
    if (!activeItinerary.value) return [];
    const members = [];
    if (activeItinerary.value.owner) {
        members.push(activeItinerary.value.owner);
    }
    if (activeItinerary.value.collaborators) {
        members.push(...activeItinerary.value.collaborators);
    }
    if (members.length === 0 && localUser.value) {
        members.push(localUser.value);
    }
    return members;
});

const fetchUser = async () => {
  if (!currentUserId.value) {
    error.value = "您尚未登入，請先登入！";
    return;
  }
  try {
    loading.value = true;
    error.value = null;
    const response = await api.get(`/api/users/${currentUserId.value}`);
    localUser.value = response.data;
    await fetchItineraries();
  } catch (err) {
    console.error(err);
    error.value = "無法取得資料，請確認後端是否啟動。";
  } finally {
    loading.value = false;
  }
};

const fetchItineraries = async () => {
    try {
        const res = await api.get(`/api/itineraries/user/${currentUserId.value}`);
        itineraries.value = res.data;
        
        if (activeItinerary.value) {
            const found = itineraries.value.find(i => i.id === activeItinerary.value.id);
            if (found) {
                activeItinerary.value = found;
            } else {
                activeItinerary.value = null; 
            }
        }
    } catch (e) {
        console.error("抓取行程失敗", e);
    }
};

const selectItinerary = (itin) => {
    activeItinerary.value = itin;
};

const createItinerary = async () => {
    if (!newItineraryForm.title) return alert("請輸入行程名稱");
    try {
        const payload = {
            ...newItineraryForm,
            owner_user_id: currentUserId.value,
            spot_ids: []
        };
        await api.post(`/api/itineraries/`, payload);
        
        alert("行程建立成功！");
        isCreatingItinerary.value = false;
        Object.assign(newItineraryForm, { title: '', budget: 0, travel_time: '', transport: '' });
        await fetchItineraries();
    } catch (e) {
        alert("建立失敗：" + (e.response?.data?.detail || e.message));
    }
};

const deleteItinerary = async (id) => {
    if (!confirm("確定要刪除此行程嗎？(無法復原)")) return;
    try {
        await api.delete(`/api/itineraries/${id}`);
        await fetchItineraries();
        if (activeItinerary.value?.id === id) activeItinerary.value = null;
    } catch (e) {
        alert("刪除失敗");
    }
};

const deleteSpotFromItinerary = async (itemId) => {
    if (!confirm("確定要從行程移除此景點嗎？")) return;
    try {
        await api.delete(`/api/itineraries/item/${itemId}`);
        await fetchItineraries(); 
    } catch (e) {
        alert("移除失敗");
    }
};

// --- 👇 景點時間與排序邏輯 👇 ---

// 儲存單一景點的時間變更
const updateSpotTime = async (item) => {
    try {
        // 呼叫後端 API 儲存時間 (請確保後端對應的路由能接收 visit_time 欄位)
        await api.put(`/api/itineraries/item/${item.id}`, { 
            visit_time: item.visit_time 
        });
    } catch (e) {
        console.error("更新時間失敗", e);
        // 若後端還沒寫好這支 API，可以在這裡提示
    }
};

// 一鍵按時間重新排序
const sortSpotsByTime = () => {
    if (!activeItinerary.value || !activeItinerary.value.spots) return;
    
    activeItinerary.value.spots.sort((a, b) => {
        // 處理空時間 (沒填時間的放到最後面)
        const timeA = a.visit_time || '23:59';
        const timeB = b.visit_time || '23:59';
        return timeA.localeCompare(timeB);
    });
    
    // 排序後自動觸發儲存新順序的 API
    onDragEnd();
};

const onDragEnd = async () => {
    // 這裡保留你原本用來更新後端排序順序的 API 邏輯
};

// --- 👆 景點時間與排序邏輯 👆 ---

const getImageUrl = (id) => `https://picsum.photos/seed/${id}/200/150`; 

watch(() => props.user, (newVal) => {
  if(newVal && newVal.id) {
    fetchUser();
  } else {
    localUser.value = null;
    itineraries.value = [];
    loading.value = false;
  } 
}, { immediate: true });

const startEditing = () => {
  if (!localUser.value) return;
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
  
  formData.likes = localUser.value.likes ? JSON.parse(JSON.stringify(localUser.value.likes)) : {};
  isEditing.value = true;
};

const cancelEdit = () => { isEditing.value = false; };

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
    alert("更新失敗：" + (err.response?.data?.detail || err.message));
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '未設定';
  return new Date(dateString).toLocaleDateString();
};

const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    alert(`✅ 已複製邀請碼：${code} \n趕快傳給朋友加入協作吧！`)
  }).catch(() => {
    alert('❌ 複製失敗，請手動複製')
  })
}
</script>

<template>
  <div class="user-page-container">
    
    <div v-if="loading" class="loading">資料載入中...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="!loading && !localUser && !error" class="error">請先登入。</div>

    <div v-if="!loading && localUser">
      
      <div class="user-tabs">
        <button :class="{ active: activeTab === 'itinerary' }" @click="activeTab = 'itinerary'">🗓️ 我的行程</button>
        <button :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">👤 個人帳戶</button>
      </div>

      <div v-if="activeTab === 'itinerary'" class="tab-content">
        
        <div class="itin-header">
            <h2>我的行程 ({{ itineraries.length }})</h2>
            
            <div class="header-actions">
                <select v-model="itinSortBy" class="sort-select">
                    <option value="newest">🕒 最新建立</option>
                    <option value="oldest">🐢 最舊建立</option>
                    <option value="travel_time">📅 出發日 (近到遠)</option>
                </select>
                
                <button @click="isCreatingItinerary = !isCreatingItinerary" class="btn-add-itin">
                    {{ isCreatingItinerary ? '取消' : '+ 建立新行程' }}
                </button>
            </div>
        </div>

        <div v-if="isCreatingItinerary" class="create-itin-card">
            <div class="form-grid">
                <div><label>行程名稱 *</label><input v-model="newItineraryForm.title" /></div>
                <div><label>預算 (TWD)</label><input type="number" v-model="newItineraryForm.budget" /></div>
                <div><label>出發日期</label><input v-model="newItineraryForm.travel_time" type="date" /></div>
                <div><label>交通方式</label><input v-model="newItineraryForm.transport" /></div>
            </div>
            <button @click="createItinerary" class="btn-primary" style="margin-top:15px">確認建立</button>
        </div>

        <div class="itin-grid">
            <div v-for="itin in sortedItineraries" :key="itin.id" 
                 class="itin-card" 
                 :class="{ active: activeItinerary?.id === itin.id }"
                 @click="selectItinerary(itin)">
                
                <div class="itin-card-top">
                    <h4 class="itin-title">{{ itin.title }}</h4>
                    <button @click.stop="deleteItinerary(itin.id)" class="btn-delete-itin">🗑️</button>
                </div>
                
                <div class="itin-date" v-if="itin.travel_time">
                    📅 {{ formatDate(itin.travel_time) }} 出發
                </div>
                
                <div class="members-display">
                    <div class="owner-tag" v-if="itin.owner">👑 {{ itin.owner.name }}</div>
                    <div v-if="itin.collaborators?.length > 0" class="collab-list">
                        <span v-for="user in itin.collaborators" :key="user.id" class="collab-tag">👤 {{ user.name }}</span>
                    </div>
                </div>

                <div class="itin-meta">
                    <p>{{ itin.spots?.length || 0 }} 個景點</p>
                    <button class="btn-copy-code" v-if="itin.code" @click.stop="copyCode(itin.code)">🔗 複製邀請碼</button>
                </div>
            </div>
            <div v-if="itineraries.length === 0" class="empty-hint">尚未建立行程</div>
        </div>

        <div v-if="activeItinerary" class="itin-detail-area">
            
            <div class="itin-detail-header">
                <h3>📍 {{ activeItinerary.title }}</h3>
                <button @click="sortSpotsByTime" class="btn-sort-time" title="依據你設定的時間重新排序">
                   🕒 自動按時間排序
                </button>
            </div>
            
            <draggable v-model="activeItinerary.spots" item-key="id" @end="onDragEnd" class="spots-list">
                <template #item="{ element }">
                    <div class="spot-item">
                        <div class="drag-handle">☰</div>
                        
                        <input 
                            type="time" 
                            v-model="element.visit_time" 
                            @change="updateSpotTime(element)"
                            class="spot-time-input"
                            title="預計抵達時間"
                        />

                        <img :src="getImageUrl(element.spot.id)" class="spot-thumb">
                        <div class="spot-content">
                            <strong>{{ element.spot.name }}</strong>
                            <p>{{ element.spot.location }}</p>
                        </div>
                        <button @click="deleteSpotFromItinerary(element.id)" class="btn-remove-spot">✕</button>
                    </div>
                </template>
            </draggable>

            <div v-if="(!activeItinerary.spots || activeItinerary.spots.length === 0)" class="empty-spots">
                此行程還沒有景點，快去首頁探索吧！
            </div>  

            <div class="divider"></div>
            <ExpenseSection :itineraryId="activeItinerary.id" :members="allMembers" />
        </div>
      </div>

      <div v-if="activeTab === 'profile'" class="tab-content">
        <div class="profile-container">
            <div class="profile-card">
                <h3>帳戶基本資料</h3>
                <div v-if="!isEditing" class="view-mode">
                    <div class="info-item"><label>姓名</label><span>{{ localUser.name || '未設定' }}</span></div>
                    <div class="info-item"><label>電子信箱</label><span>{{ localUser.email }}</span></div>
                    <div class="info-item"><label>聯絡電話</label><span>{{ localUser.phone || '未設定' }}</span></div>
                    <div class="info-item"><label>生日</label><span>{{ formatDate(localUser.birthday) }}</span></div>
                    <button @click="startEditing" class="btn-edit-outline">編輯帳戶資料</button>
                </div>

                <div v-else class="edit-mode">
                    <div class="form-group"><label>姓名</label><input v-model="formData.name" /></div>
                    <div class="form-group">
                        <label>電話</label>
                        <div class="phone-input-group" style="display:flex; gap:10px;">
                            <select v-model="formData.phonePrefix" style="width:120px;">
                                <option v-for="c in countryCodes" :key="c.code" :value="c.code">{{ c.label }}</option>
                            </select>
                            <input v-model="formData.phoneNumber" style="flex:1;" />
                        </div>
                    </div>
                    <div class="form-group"><label>生日</label><input v-model="formData.birthday" type="date" /></div>
                    <div class="button-group" style="display:flex; gap:10px; margin-top:20px;">
                        <button @click="saveUser" class="btn-primary" style="flex:1;">儲存變更</button>
                        <button @click="cancelEdit" class="btn-cancel" style="flex:1;">取消</button>
                    </div>
                </div>
            </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.user-page-container { max-width: 1000px; margin: 0 auto; padding: 20px; }

.user-tabs { display: flex; gap: 30px; border-bottom: 1px solid var(--border-color); margin-bottom: 30px; }
.user-tabs button { background: none; border: none; padding: 15px 5px; font-size: 1.1rem; font-weight: bold; color: var(--text-secondary); cursor: pointer; position: relative; }
.user-tabs button.active { color: var(--primary-color); }
.user-tabs button.active::after { content: ''; position: absolute; bottom: -1px; left: 0; width: 100%; height: 3px; background-color: var(--primary-color); }
.tab-content { animation: fadeIn 0.3s ease; }

/* 行程標題與排序下拉選單 */
.itin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;}
.header-actions { display: flex; align-items: center; gap: 15px; }
.sort-select { padding: 8px 12px; border-radius: 20px; border: 1px solid var(--border-color); background-color: var(--card-bg); color: var(--text-color); font-size: 0.9rem; cursor: pointer; outline: none; width: auto !important; }
.sort-select:hover { border-color: var(--primary-color); }
.btn-add-itin { background: var(--primary-color); color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-weight: bold;}

.create-itin-card { background: var(--card-bg); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid var(--border-color);}
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.form-grid label { display: block; margin-bottom: 5px; color: var(--text-secondary); font-size: 0.9rem;}
.form-grid input { width: 100%; padding: 10px; border: 1px solid var(--input-border); border-radius: 8px; box-sizing: border-box; background: var(--input-bg); color: var(--text-color);}

.itin-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-top: 10px; }
.itin-card { padding: 20px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; cursor: pointer; transition: all 0.2s; display: flex; flex-direction: column; justify-content: space-between; min-height: 150px;}
.itin-card:hover { border-color: var(--primary-color); transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.05);}
.itin-card.active { border: 2px solid var(--primary-color); background: rgba(50, 100, 255, 0.03); }

.itin-card-top { display: flex; justify-content: space-between; align-items: flex-start; }
.itin-title { margin: 0 0 10px 0; font-size: 1.15rem; color: var(--text-color); line-height: 1.4;}
.btn-delete-itin { background: none; border: none; cursor: pointer; font-size: 1.1rem; color: #ccc; padding: 0;}
.btn-delete-itin:hover { color: #e74c3c; }

.itin-date { font-size: 0.85rem; color: var(--primary-color); font-weight: bold; margin-bottom: 10px; }

.members-display { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 15px; }
.owner-tag { font-size: 0.75rem; background-color: #fff8e1; color: #f57c00; padding: 2px 8px; border-radius: 10px; border: 1px solid #ffe0b2; }
.collab-list { display: flex; flex-wrap: wrap; gap: 5px; }
.collab-tag { font-size: 0.75rem; background-color: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 10px; border: 1px solid #bbdefb; }

.itin-meta { display: flex; justify-content: space-between; align-items: center; margin-top: auto; border-top: 1px dashed var(--border-color); padding-top: 12px;}
.itin-meta p { margin: 0; font-size: 0.9rem; color: var(--text-secondary); font-weight: bold;}
.btn-copy-code { background: rgba(50, 100, 255, 0.1); color: var(--primary-color); border: none; padding: 5px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; cursor: pointer; transition: all 0.2s ease; }
.btn-copy-code:hover { background: var(--primary-color); color: white; transform: scale(1.05); }

/* ✨ 行程詳情與時間排序區塊 */
.itin-detail-area { background: var(--card-bg); padding: 30px; border-radius: 16px; border: 1px solid var(--border-color); margin-top: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.05);}
.itin-detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;}
.itin-detail-header h3 { margin: 0; color: var(--text-color); font-size: 1.4rem;}
.btn-sort-time { background: rgba(50, 100, 255, 0.1); color: var(--primary-color); border: 1px solid var(--primary-color); padding: 6px 12px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.2s; font-size: 0.9rem;}
.btn-sort-time:hover { background: var(--primary-color); color: white;}

.spots-list { margin-bottom: 30px; }
.spot-item { display: flex; align-items: center; background: var(--input-bg); border: 1px solid var(--border-color); padding: 12px; margin-bottom: 12px; border-radius: 10px; transition: background 0.2s; }
.spot-item:hover { background: var(--card-bg); box-shadow: 0 2px 8px rgba(0,0,0,0.05);}
.drag-handle { color: #ccc; cursor: grab; font-size: 1.2rem; padding: 0 10px;}

/* ✨ 時間輸入框樣式 */
.spot-time-input { 
    margin-right: 15px; 
    padding: 6px 10px; 
    border-radius: 8px; 
    border: 1px solid var(--border-color); 
    background: var(--card-bg); 
    color: var(--text-color); 
    font-family: inherit; 
    font-size: 0.95rem;
    cursor: pointer;
    transition: 0.2s;
}
.spot-time-input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(50, 100, 255, 0.1);}

.spot-thumb { width: 70px; height: 50px; object-fit: cover; border-radius: 6px; margin-right: 15px; }
.spot-content { flex: 1; }
.spot-content strong { color: var(--text-color); font-size: 1.05rem;}
.spot-content p { margin: 4px 0 0; font-size: 0.85rem; color: var(--text-secondary); }
.btn-remove-spot { background: none; border: none; color: #aaa; cursor: pointer; font-size: 1.2rem; }
.btn-remove-spot:hover { color: #e74c3c; }
.divider { height: 1px; background-color: var(--border-color); margin: 30px 0; }
.empty-hint, .empty-spots { text-align: center; color: var(--text-secondary); padding: 30px; border: 2px dashed var(--border-color); border-radius: 12px; }

/* 個人資料卡片 */
.profile-container { display: flex; justify-content: center; }
.profile-card { background: var(--card-bg); padding: 40px; border-radius: 16px; width: 100%; max-width: 600px; border: 1px solid var(--border-color); box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
.profile-card h3 { margin-top: 0; color: var(--text-color);}
.info-item { display: flex; justify-content: space-between; padding: 16px 0; border-bottom: 1px solid var(--border-color); font-size: 1.05rem;}
.info-item label { color: var(--text-secondary); }
.info-item span { font-weight: 500; color: var(--text-color); }
.btn-edit-outline { margin-top: 30px; width: 100%; background: none; border: 1px solid var(--primary-color); color: var(--primary-color); padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s;}
.btn-edit-outline:hover { background: rgba(50, 100, 255, 0.05); }

.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: bold; color: var(--text-secondary); font-size: 0.9rem;}
.form-group input, .form-group select { width: 100%; padding: 12px; border: 1px solid var(--input-border); border-radius: 8px; background-color: var(--input-bg); color: var(--text-color); box-sizing: border-box;}
.btn-cancel { background: #f1f1f1; color: #666; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s;}
.btn-cancel:hover { background: #e2e2e2; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* RWD微調 */
@media (max-width: 768px) {
  .spot-item { flex-wrap: wrap; gap: 10px; }
  .spot-time-input { width: 100%; margin-right: 0; margin-bottom: 5px; }
}
</style>