<template>
  <div class="login-container">
    <el-card class="login-card" style="width: 400px;">
      <template #header>
        <div class="login-title">游戏环境净化平台</div>
      </template>

      <el-form :model="loginForm">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入账号"
            :prefix-icon="User"
            readonly
            class="login-input"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            readonly
            class="login-input"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%;"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="demo-account">
        <p>演示账号：admin / 123456</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()

// 登录表单数据
const loginForm = reactive({
  username: 'admin',
  password: '123456'
})

// 登录处理
const handleLogin = () => {
  ElMessage.success('登录成功')
  router.push('/dashboard')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0A0F1F 0%, #1A1D2A 100%);
  padding: 20px;
}

.login-card {
  background-color: #1A1D2A;
  border: 1px solid #2A2F3A;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin: 0;
}

.login-input {
  background-color: #2A2F3A;
  border: 1px solid #3A3F4A;
  color: #B0B3C1;
}

.login-input :deep(.el-input__inner) {
  background-color: #2A2F3A;
  border: none;
  color: #B0B3C1;
}

.login-input :deep(.el-input__inner::placeholder) {
  color: #7A7F8A;
}

.login-input :deep(.el-input__prefix) {
  color: #7A7F8A;
}

.demo-account {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #2A2F3A;
}

.demo-account p {
  color: #7A7F8A;
  font-size: 14px;
  margin: 0;
}

:deep(.el-card__header) {
  background-color: #1A1D2A;
  border-bottom: 1px solid #2A2F3A;
  padding: 20px;
}

:deep(.el-card__body) {
  padding: 30px 20px;
}

:deep(.el-form-item__error) {
  color: #F56C6C;
}
</style>