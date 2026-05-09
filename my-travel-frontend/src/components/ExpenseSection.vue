<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import api from '../api/axios.js';

const props = defineProps({
  itineraryId: {
    type: String,
    required: true
  },
  // 從上層 (User.vue) 傳進來的協作者名單 + 房主，用來當作付款人選單
  members: {
    type: Array,
    required: true
  }
});

const expenses = ref([]);
const isLoading = ref(false);
const isAddingExpense = ref(false);

// 新增花費的表單狀態
const newExpense = reactive({
  payer_id: '',
  description: '',
  amount: 0,
  currency: 'TWD',
  // 這就是對應你後端 schemas 的 List[SplitDetail]
  split_details: [] 
});

// 抓取此行程的所有記帳紀錄
const fetchExpenses = async () => {
    // 我們稍後需要在後端補上這支 GET API
    try {
        const res = await api.get(`/api/expenses/itinerary/${props.itineraryId}`);
        expenses.value = res.data;
    } catch (e) {
        console.error("無法抓取記帳紀錄", e);
    }
};

// 進入頁面或行程切換時，重新抓資料
watch(() => props.itineraryId, () => {
    fetchExpenses();
}, { immediate: true });

// --- 分攤名單動態邏輯 ---

// 新增一個分攤人員到清單中
const addSplitPerson = () => {
  newExpense.split_details.push({
    user_id: '',
    amount: 0
  });
};

// 移除清單中的某個人
const removeSplitPerson = (index) => {
  newExpense.split_details.splice(index, 1);
};

// UX 魔法：計算目前分攤總和，用來防呆
const totalSplitAmount = computed(() => {
    return newExpense.split_details.reduce((sum, item) => sum + (Number(item.amount) || 0), 0);
});

// 送出表單
const submitExpense = async () => {
    if (!newExpense.description || newExpense.amount <= 0 || !newExpense.payer_id) {
        alert("請填寫完整的花費描述、金額與付款人！");
        return;
    }

    if (newExpense.split_details.length === 0) {
        alert("至少需要一位分攤者！");
        return;
    }

    // 防呆檢查：分攤總和必須等於總金額
    if (totalSplitAmount.value !== newExpense.amount) {
        alert(`分攤總額 ($${totalSplitAmount.value}) 與總花費 ($${newExpense.amount}) 不符！請調整。`);
        return;
    }

    try {
        isLoading.value = true;
        // 將資料整理成後端 schemas 要求的格式
        const payload = {
            itinerary_id: props.itineraryId,
            payer_id: newExpense.payer_id,
            description: newExpense.description,
            amount: newExpense.amount,
            currency: newExpense.currency,
            split_details: newExpense.split_details.map(d => ({
                user_id: d.user_id,
                amount: Number(d.amount)
            }))
        };

        await api.post('/api/expenses/', payload);
        alert("記帳成功！");
        
        // 重置表單並重新抓資料
        isAddingExpense.value = false;
        Object.assign(newExpense, { payer_id: '', description: '', amount: 0, split_details: [] });
        await fetchExpenses();

    } catch (e) {
        alert("記帳失敗：" + (e.response?.data?.detail || e.message));
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
  <div class="expense-section">
    <div class="expense-header">
      <h3>💸 記帳明細</h3>
      <button @click="isAddingExpense = !isAddingExpense" class="btn-add">
        {{ isAddingExpense ? '取消記帳' : '+ 新增一筆' }}
      </button>
    </div>

    <div v-if="isAddingExpense" class="expense-form-card">
      <div class="form-row">
        <div class="input-group">
          <label>花費描述</label>
          <input v-model="newExpense.description" placeholder="例如：高鐵票、晚餐" />
        </div>
        <div class="input-group">
          <label>總金額</label>
          <input v-model.number="newExpense.amount" type="number" min="0" />
        </div>
      </div>

      <div class="form-row">
        <div class="input-group">
          <label>誰先付款的？ (墊錢的人)</label>
          <select v-model="newExpense.payer_id">
            <option value="" disabled>請選擇付款人</option>
            <option v-for="member in members" :key="member.id" :value="member.id">
              {{ member.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="split-details-area">
        <div class="split-header">
            <label>如何分攤這筆錢？</label>
            <span class="split-status" :class="{ 'error': totalSplitAmount !== newExpense.amount }">
                目前分攤總和: ${{ totalSplitAmount }} / 總花費: ${{ newExpense.amount }}
            </span>
        </div>
        
        <div v-for="(detail, index) in newExpense.split_details" :key="index" class="split-row">
            <select v-model="detail.user_id" class="split-user-select">
                <option value="" disabled>選擇人員</option>
                <option v-for="member in members" :key="member.id" :value="member.id">
                    {{ member.name }}
                </option>
            </select>
            <span class="currency-symbol">$</span>
            <input v-model.number="detail.amount" type="number" class="split-amount-input" placeholder="分攤金額" />
            <button @click="removeSplitPerson(index)" class="btn-remove-split">✕</button>
        </div>

        <button @click="addSplitPerson" class="btn-add-split">+ 加入分攤人員</button>
      </div>

      <button @click="submitExpense" class="btn-submit" :disabled="isLoading || totalSplitAmount !== newExpense.amount">
        {{ isLoading ? '儲存中...' : '確認記帳' }}
      </button>
    </div>

    <div class="expense-list">
      <div v-for="exp in expenses" :key="exp.id" class="expense-item">
        <div class="exp-main">
            <strong>{{ exp.description }}</strong>
            <span class="exp-amount">${{ exp.amount }}</span>
        </div>
        <div class="exp-meta">
            付款人: {{ members.find(m => m.id === exp.payer_id)?.name || '未知' }} | 
            {{ new Date(exp.created_at).toLocaleDateString() }}
        </div>
      </div>
      <div v-if="expenses.length === 0 && !isAddingExpense" class="empty-state">
        目前還沒有任何花費紀錄喔！
      </div>
    </div>
  </div>
</template>

<style scoped>
.expense-section { margin-top: 10px; }
.expense-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.btn-add { background: var(--primary-color); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
.expense-form-card { background: var(--input-bg); padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px dashed var(--primary-color); }
.form-row { display: flex; gap: 15px; margin-bottom: 10px; }
.input-group { flex: 1; }
.input-group label { display: block; margin-bottom: 5px; font-size: 0.9rem; color: var(--text-secondary); }
.input-group input, .input-group select { width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; box-sizing: border-box; }

.split-details-area { background: var(--card-bg); padding: 10px; border-radius: 6px; margin: 15px 0; border: 1px solid var(--border-color); }
.split-header { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.9rem;}
.split-status.error { color: #e74c3c; font-weight: bold; }
.split-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.split-user-select { flex: 2; padding: 6px; }
.currency-symbol { font-weight: bold; color: var(--text-secondary); }
.split-amount-input { flex: 1; padding: 6px; }
.btn-remove-split { background: none; border: none; color: #e74c3c; cursor: pointer; font-weight: bold; }
.btn-add-split { width: 100%; background: none; border: 1px dashed #ccc; padding: 8px; color: #666; cursor: pointer; border-radius: 4px; }
.btn-add-split:hover { background: #eee; }

.btn-submit { width: 100%; background: var(--primary-color); color: white; padding: 10px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }

.expense-item { padding: 12px; border-bottom: 1px solid var(--border-color); }
.exp-main { display: flex; justify-content: space-between; margin-bottom: 4px; }
.exp-amount { font-weight: bold; color: #e74c3c; }
.exp-meta { font-size: 0.85rem; color: var(--text-secondary); }
.empty-state { text-align: center; color: var(--text-secondary); padding: 20px; font-style: italic; }
</style>