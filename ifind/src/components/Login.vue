<template>
  <div class="login-container">
    <div class="login-box">
      <h2>用户登录</h2>
      <form @submit="handleLogin">
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
        <button type="submit" class="login-btn" >登录</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      form: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    handleLogin() {
      // 这里要改掉成登录的命令我这里没连接数据库就直接实现跳转作演示用



      this.$router.replace('/Main').catch(err => {
        if (err.name !== 'NavigationDuplicated') {
          console.error('导航错误:', err)
        }
      })
    }
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