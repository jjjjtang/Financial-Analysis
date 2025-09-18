<template>
  <div class="login-container">
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

      <div style="margin-top: 10px; text-align: center;">
        <span v-if="!isRegister">还没有账号？</span>
        <span v-else>已有账号？</span>
        <el-button type="text" @click="toggleMode">
          {{ isRegister ? '去登录' : '去注册' }}
        </el-button>
      </div>
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
  user_id: '',       // 注册时使用
  username: '',
  password: ''
})

// 切换登录/注册模式
function toggleMode() {
  isRegister.value = !isRegister.value
  form.user_id = ''
  form.username = ''
  form.password = ''
}

async function handleSubmit() {
  try {
    if (isRegister.value) {
      // 注册请求
      const res = await http.post('/users/register', {
        user_id: form.user_id,
        username: form.username,
        password: form.password
      })
      alert(res.data.message || '注册成功')
      // 注册完成后切换到登录
      isRegister.value = false
      form.user_id = ''
      form.username = ''
      form.password = ''
    } else {
      // 登录请求
      const res = await http.post('/users/login', {
        username: form.username,
        password: form.password
      })
      if (res.data.message === '登录成功') {
        alert('登录成功！')
        console.log(res.data)
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
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.login-box h2 {
  margin-bottom: 30px;
  text-align: center;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  border-color: #409eff;
  outline: none;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #66b1ff;
}
</style>
