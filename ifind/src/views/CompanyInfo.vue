<template>
  <div class="company-container">
    <h2>公司信息</h2>

    <!-- Logo 和公司名称 -->
    <div class="header">
      <img :src="logo" alt="公司Logo" class="logo" />
      <div class="company-name">{{ name }}</div>
    </div>

    <!-- 联系方式 -->
    <div class="contact">
      <div class="contact-item">
        <strong>电话：</strong> {{ phone }}
      </div>
      <div class="contact-item">
        <strong>二维码：</strong>
        <img :src="qrcode" alt="二维码" class="qrcode" />
      </div>
    </div>

    <!-- 预留照片框 -->
    <div class="photos">
      <div class="photo-box" v-for="(photo, index) in photos" :key="index">
        <img :src="photo" alt="预留照片" />
        <div class="photo-label">预留照片 {{ index + 1 }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 我这里预留了位置用来后面添加
const logo = ref('')
const name = ref('示例公司有限公司')
const phone = ref('123-4567-8901')
const qrcode = ref('https://via.placeholder.com/120x120?text=微信名片')

// 预留照片数组
const photos = ref([
  '',
])
</script>

<style scoped>
.company-container {
  padding: 20px;
  background: #fff;
  min-height: 100%;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  margin-right: 20px;
}

.company-name {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.contact {
  display: flex;
  gap: 40px;
  margin-bottom: 30px;
  align-items: center;
}

.contact-item {
  font-size: 16px;
}

.qrcode {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  margin-left: 10px;
}

.photos {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.photo-box {
  width: 200px;
  text-align: center;
}

.photo-box img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
}

.photo-label {
  margin-top: 5px;
  font-size: 14px;
  color: #606266;
}
</style>
