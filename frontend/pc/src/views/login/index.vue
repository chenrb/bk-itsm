<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">ITSM 登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="login-field">
          <label>用户名</label>
          <input
            ref="usernameInput"
            v-model="form.username"
            type="text"
            autocomplete="username"
            :disabled="loading"
            placeholder="请输入用户名"
          />
        </div>
        <div class="login-field">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            :disabled="loading"
            placeholder="请输入密码"
          />
        </div>
        <p v-if="errorMsg" class="login-error">{{ errorMsg }}</p>
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Cookies from 'js-cookie';

function getCSRFToken() {
  const match = document.cookie.match(/(?:^|;\s*)itsm_csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : '';
}

export default {
  name: 'LoginPage',
  data() {
    return {
      form: { username: '', password: '' },
      loading: false,
      errorMsg: '',
    };
  },
  mounted() {
    document.title = '登录 - ITSM';
    this.$refs.usernameInput?.focus();
  },
  methods: {
    async handleLogin() {
      this.errorMsg = '';
      if (!this.form.username || !this.form.password) {
        this.errorMsg = '请输入用户名和密码';
        return;
      }

      this.loading = true;
      try {
        const csrfToken = getCSRFToken();
        await axios.post('/account/login/', this.form, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
        });

        // Login success — fetch user data via init
        const store = this.$store;
        const response = await store.dispatch('getPlatformPreData');

        if (response) {
          store.dispatch('user/syncPermissions');
          this.$router.push('/');
        }
      } catch (err) {
        if (err.response && err.response.data && err.response.data.message) {
          this.errorMsg = err.response.data.message;
        } else {
          this.errorMsg = '登录失败，请重试';
        }
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
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

  label {
    display: block;
    margin-bottom: 6px;
    font-size: 14px;
    color: #63656e;
  }

  input {
    width: 100%;
    height: 40px;
    padding: 0 12px;
    border: 1px solid #c4c6cc;
    border-radius: 2px;
    font-size: 14px;
    outline: none;
    box-sizing: border-box;

    &:focus {
      border-color: #3a84ff;
    }

    &:disabled {
      background: #fafafa;
      cursor: not-allowed;
    }
  }
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

  &:hover {
    background: #699df4;
  }

  &:disabled {
    background: #dcdee5;
    cursor: not-allowed;
  }
}
</style>
