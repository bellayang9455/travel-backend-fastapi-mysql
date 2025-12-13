<template>
  <div class="user-profile-container">
    <h1>個人資料</h1>

    <div v-if="loading" class="loading">資料載入中...</div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="!loading && user" class="profile-card">
      
      <div v-if="!isEditing">
        <div class="info-group">
          <label>Email：</label>
          <span>{{ user.email }}</span>
        </div>
        <div class="info-group">
          <label>姓名：</label>
          <span>{{ user.name || '未設定' }}</span>
        </div>
        <div class="info-group">
          <label>電話：</label>
          <span>{{ user.phone || '未設定' }}</span>
        </div>
        <div class="info-group">
          <label>生日：</label>
          <span>{{ formatDate(user.birthday) }}</span>
        </div>
        
        <div class="info-group">
          <label>喜好 (JSON)：</label>
          <div class="tags">
            <span v-for="(value, key) in user.likes" :key="key" class="tag">
              {{ key }}: {{ value }}
            </span>
            <span v-if="!user.likes || Object.keys(user.likes).length === 0">尚無資料</span>
          </div>
        </div>

        <button @click="startEditing" class="btn-primary">編輯資料</button>
      </div>

      <div v-else class="edit-form">
        <div class="form-group">
          <label>Email (不可修改)</label>
          <input type="text" :value="user.email" disabled class="input-disabled" />
        </div>

        <div class="form-group">
          <label>姓名</label>
          <input v-model="formData.name" type="text" />
        </div>

        <div class="form-group">
          <label>電話</label>
          <input v-model="formData.phone" type="text" />
        </div>

        <div class="form-group">
          <label>生日</label>
          <input v-model="formData.birthday" type="date" />
        </div>

        <div class="form-group">
          <label>喜好的食物 (儲存於 JSON 欄位)</label>
          <input v-model="formData.likes.food" type="text" placeholder="例如：拉麵" />
        </div>

        <div class="button-group">
          <button @click="saveUser" class="btn-save">儲存</button>
          <button @click="cancelEdit" class="btn-cancel">取消</button>
        </div>
      </div>

    </div>
  </div>
</template>