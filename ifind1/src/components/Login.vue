<template>
  <div class="login-container">
    <!-- 顶部标题栏 -->
    <header class="login-header">
      <div class="logo-placeholder">
        <img src="../../public/logo.png" style="height: 50px;width: 50px">
      </div>
      <h1 class="system-title">金融财报分析系统</h1>
    </header>

    <!-- 登录卡片 -->
    <div class="login-box">
      <h2>{{ isRegister ? '用户注册' : '用户登录' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div v-if="isRegister" class="form-group">
          <label for="user_id">用户ID</label>
          <input
              type="number"
              id="user_id"
              v-model="form.user_id"
              placeholder="请输入用户ID"
              required
          />
        </div>
        <div class="form-group">
          <label for="username">用户名</label>
          <input
              type="text"
              id="username"
              v-model="form.username"
              placeholder="请输入用户名"
              required
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
              type="password"
              id="password"
              v-model="form.password"
              placeholder="请输入密码"
              required
          />
        </div>
        <button type="submit" class="login-btn">
          {{ isRegister ? '注册' : '登录' }}
        </button>
      </form>

      <div class="toggle-box">
        <span>{{ isRegister ? '已有账号？' : '还没有账号？' }}</span>
        <el-button type="text" @click="toggleMode">
          {{ isRegister ? '去登录' : '去注册' }}
        </el-button>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="background-decor decor-top-left"></div>
    <div class="background-decor decor-bottom-right"></div>

    <!-- 背景金融折线插画 -->
    <div class="background-illustration">
      <svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
        <polyline
            points="0,400 100,320 200,350 300,260 400,300 500,180"
            fill="none"
            stroke="#409eff"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
            opacity="0.6"
        />
        <circle cx="100" cy="320" r="6" fill="#409eff" opacity="0.8"/>
        <circle cx="200" cy="350" r="6" fill="#409eff" opacity="0.8"/>
        <circle cx="300" cy="260" r="6" fill="#409eff" opacity="0.8"/>
        <circle cx="400" cy="300" r="6" fill="#409eff" opacity="0.8"/>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/api/http'

const router = useRouter()
const isRegister = ref(false)

const form = reactive({
  user_id: '',
  username: '',
  password: ''
})

function toggleMode() {
  isRegister.value = !isRegister.value
  form.user_id = ''
  form.username = ''
  form.password = ''
}

async function handleSubmit() {
  try {
    if (isRegister.value) {
      const res = await http.post('/users/register', {
        user_id: form.user_id,
        username: form.username,
        password: form.password
      })
      alert(res.data.message || '注册成功')
      isRegister.value = false
      form.user_id = ''
      form.username = ''
      form.password = ''
    } else {
      const res = await http.post('/users/login', {
        username: form.username,
        password: form.password
      })
      if (res.data.message === '登录成功') {
        alert('登录成功！')
        localStorage.setItem('isAuthenticated', 'true')
        router.replace('/home').catch(err => {
          if (err.name !== 'NavigationDuplicated') console.error(err)
        })
      } else {
        alert(res.data.message || '登录失败')
      }
    }
  } catch (err) {
    console.error('请求失败:', err)
    alert('网络或后端服务异常')
  }
}
</script>

<style scoped>
/* 背景整体 */
.login-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #e6f0ff, #ffffff);
  align-items: center;
  position: relative;
  overflow: hidden;
}

/* 顶部标题栏 */
.login-header {
  width: 100%;
  height: 80px;
  display: flex;
  align-items: center;
  padding-left: 10%;
  background: rgba(255, 254, 253, 0.80);
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  z-index: 2;
}

.logo-placeholder {
  width: 50px;
  height: 50px;
  background-color: #dcdcdc;
  border-radius: 50%;
  margin-right: 16px;
}

.system-title {
  font-size: 26px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 1px;
}

/* 登录卡片 */
.login-box {
  margin-top: 10vh;
  width: 420px;
  padding: 40px;
  background: rgba(255, 254, 253, 0.80);
  border-radius: 14px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.1);
  z-index: 2;
}

.login-box h2 {
  margin-bottom: 25px;
  text-align: center;
  color: #333;
  font-size: 22px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  border-color: #409eff;
  outline: none;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.login-btn:hover {
  background: #66b1ff;
}

.toggle-box {
  margin-top: 15px;
  text-align: center;
  color: #666;
}

/* 背景装饰圆形 */
.background-decor {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
  z-index: 0;
}

.decor-top-left {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  background: #a5d8ff;
}

.decor-bottom-right {
  width: 350px;
  height: 350px;
  bottom: -120px;
  right: -120px;
  background: #91a7ff;
}

/* 金融折线插画 */
.background-illustration {
  position: absolute;
  bottom: 100px;
  right: 40px;
  width: 480px;
  height: 260px;
  opacity: 0.25;
  z-index: 1;
}
</style>