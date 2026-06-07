<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">ITSM</h2>
      <form @submit.prevent="handleLogin">
        <div class="login-field">
          <label>用户名</label>
          <input v-model="username" type="text" autocomplete="username" placeholder="请输入用户名" required autofocus>
        </div>
        <div class="login-field">
          <label>密码</label>
          <input v-model="password" type="password" autocomplete="current-password" placeholder="请输入密码" required>
        </div>
        <p v-if="error" class="login-error">{{ error }}</p>
        <button type="submit" class="login-btn" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
      </form>
    </div>
  </div>
</template>

<script>
  import ajax from '@/utils/ajax';

  export default {
    name: 'Login',
    data() {
      return {
        username: '',
        password: '',
        error: '',
        loading: false,
      };
    },
    methods: {
      async handleLogin() {
        this.error = '';
        this.loading = true;
        try {
          const res = await ajax.post('auth/login/', {
            username: this.username,
            password: this.password,
          });
          if (res.data && res.data.result) {
            window.location.href = window.location.pathname + '#/';
          } else {
            this.error = (res.data && res.data.msg) || '登录失败';
          }
        } catch (e) {
          // 拦截器 reject 的可能是 axios response 对象
          const data = e.data || (e.response && e.response.data);
          if (data && data.message) {
            this.error = data.message;
          } else if (data && data.msg) {
            this.error = data.msg;
          } else {
            this.error = '网络错误，请重试';
          }
        } finally {
          this.loading = false;
        }
      },
    },
  };
</script>

<style scoped>
  .login-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #f5f7fa;
  }
  .login-card {
    width: 400px;
    padding: 40px;
    background: #fff;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  .login-title {
    text-align: center;
    margin: 0 0 30px;
    font-size: 22px;
    color: #313238;
  }
  .login-field {
    margin-bottom: 20px;
  }
  .login-field label {
    display: block;
    margin-bottom: 6px;
    font-size: 14px;
    color: #63656e;
  }
  .login-field input {
    width: 100%;
    height: 40px;
    padding: 0 12px;
    border: 1px solid #c4c6cc;
    border-radius: 2px;
    font-size: 14px;
    outline: none;
  }
  .login-field input:focus {
    border-color: #3a84ff;
  }
  .login-error {
    margin: 0 0 16px;
    color: #ea3636;
    font-size: 13px;
  }
  .login-btn {
    width: 100%;
    height: 40px;
    background: #3a84ff;
    color: #fff;
    border: none;
    border-radius: 2px;
    font-size: 14px;
    cursor: pointer;
  }
  .login-btn:hover {
    background: #699df4;
  }
  .login-btn:disabled {
    background: #c4c6cc;
    cursor: not-allowed;
  }
</style>
