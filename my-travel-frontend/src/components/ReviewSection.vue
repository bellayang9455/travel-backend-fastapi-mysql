<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import api from '../api/axios.js';

const props = defineProps({
  spotId: { type: String, required: true },
  user: { type: Object, default: null }
});

const reviews = ref([]);
const loading = ref(false);
const newReview = ref({
  stars: 5,
  content: ''
});

// ✨ 設定最大字數限制為 30
const maxLength = 30;
const charCount = computed(() => newReview.value.content.length);

// 抓取評論
const fetchReviews = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/reviews/', { params: { spot_id: props.spotId } });
    reviews.value = res.data;
  } catch (e) {
    console.error("抓取評論失敗", e);
  } finally {
    loading.value = false;
  }
};

// 送出評論
const submitReview = async () => {
  if (!props.user) return alert("請先登入！");
  if (charCount.value === 0) return alert("請輸入評論內容！");
  if (charCount.value > maxLength) return alert("評論字數超過限制！");

  try {
    const payload = {
      user_id: props.user.id,
      spot_id: props.spotId,
      stars: newReview.value.stars,
      content: newReview.value.content,
      photos: []
    };
    await api.post('/api/reviews/', payload);
    alert("感謝您的評價！");
    newReview.value.content = '';
    fetchReviews();
  } catch (e) {
    alert("送出失敗：" + (e.response?.data?.detail || e.message));
  }
};

onMounted(fetchReviews);

watch(() => props.spotId, fetchReviews);
</script>

<template>
  <div class="review-panel">
    <!-- 撰寫區 -->
    <div class="write-section">
      <h4>✍️ 撰寫評價 (限 30 字)</h4>
      <div class="stars-picker">
        <span 
          v-for="n in 5" :key="n" 
          @click="newReview.stars = n" 
          :class="{ active: n <= newReview.stars }"
        >★</span>
      </div>
      <!-- ✨ 使用 maxlength="30" 強制限制 -->
      <textarea 
        v-model="newReview.content" 
        :placeholder="user ? '簡單分享您的心得... (30字內)' : '請先登入以發表評論'" 
        :disabled="!user"
        maxlength="30"
      ></textarea>
      <div class="write-footer">
        <span :class="{ 'warning': charCount >= maxLength }">
          字數: {{ charCount }} / {{ maxLength }}
        </span>
        <button 
          @click="submitReview" 
          :disabled="!user || charCount === 0"
        >送出評論</button>
      </div>
    </div>

    <div class="divider"></div>

    <!-- 列表區 -->
    <div class="list-section">
      <h5>最新短評 ({{ reviews.length }})</h5>
      <div v-if="loading" class="hint">讀取中...</div>
      <div v-else-if="reviews.length === 0" class="hint">目前還沒有評論。</div>
      <div v-for="rev in reviews" :key="rev.id" class="review-card">
        <div class="rev-header">
          <strong>{{ rev.user_name || '匿名旅人' }}</strong>
          <span class="rev-stars">{{ '★'.repeat(rev.stars) }}</span>
        </div>
        <p class="rev-text">{{ rev.content }}</p>
        <span class="rev-date">{{ new Date(rev.created_at).toLocaleDateString() }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.review-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 15px;
  background: var(--bg-color);
  box-sizing: border-box;
}

.write-section h4 { margin: 0 0 10px 0; font-size: 0.95rem; }
.stars-picker { font-size: 1.4rem; color: #ddd; cursor: pointer; margin-bottom: 8px; }
.stars-picker span.active { color: #f1c40f; }

textarea {
  width: 100%;
  height: 70px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--input-bg);
  color: var(--text-color);
  resize: none;
  box-sizing: border-box;
  font-size: 0.9rem;
}

.write-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 0.8rem;
}

.write-footer span.warning { color: #e67e22; font-weight: bold; }

button {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: bold;
}

button:disabled { opacity: 0.4; cursor: not-allowed; }

.divider { height: 1px; background: var(--border-color); margin: 15px 0; }

.list-section { flex: 1; overflow-y: auto; }
.list-section h5 { margin: 0 0 10px 0; color: var(--text-secondary); font-size: 0.8rem; }

.review-card {
  background: var(--card-bg);
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-bottom: 10px;
}

.rev-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.rev-stars { color: #f1c40f; font-size: 0.8rem; }
.rev-text { font-size: 0.9rem; margin: 5px 0; line-height: 1.4; color: var(--text-color); }
.rev-date { font-size: 0.75rem; color: var(--text-secondary); }

.hint { text-align: center; padding: 20px; color: var(--text-secondary); font-style: italic; font-size: 0.85rem; }

/* 滾動條美化 */
.list-section::-webkit-scrollbar { width: 4px; }
.list-section::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; }
</style>