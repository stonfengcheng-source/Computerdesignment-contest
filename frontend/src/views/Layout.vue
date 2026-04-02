<template>
  <div class="layout-wrapper">
    <header class="top-navbar">
      <div class="nav-left">
        <div class="logo">
          <span class="logo-text">深蓝卫士</span>
        </div>
        <nav class="main-nav">
          <router-link to="/" active-class="active-link">介绍导入</router-link>
          <span class="divider">>></span>
          <router-link to="/dashboard" active-class="active-link">总览台</router-link>

          <template v-if="currentRouteName !== 'intro' && currentRouteName !== 'dashboard'">
            <span class="divider">>></span>
            <span class="active-link">{{ currentRouteTitle }}</span>
          </template>
        </nav>
      </div>

      <div class="nav-right">
        <button class="icon-btn">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
        </button>
        <button class="icon-btn">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
        </button>
        <div class="user-avatar">
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin" alt="头像" />
        </div>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 计算当前路由名称和标题，用于渲染类似面包屑的导航栏
const currentRouteName = computed(() => route.name)
const currentRouteTitle = computed(() => route.meta.title || '')
</script>

<style scoped>
.layout-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-navbar {
  height: 64px;
  background-color: #ffffff; /* 必须是纯白实色背景 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #E2E8F0;
  position: sticky;
  top: 0;
  z-index: 9999; /* 调高层级，绝对压住下方所有元素 */
}
/* 其他原有样式保持不变... */

.nav-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
  letter-spacing: 1px;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: var(--text-regular);
}

.main-nav a {
  text-decoration: none;
  color: var(--text-regular);
  transition: color 0.3s;
}

.main-nav a:hover {
  color: var(--primary-color);
}

.active-link {
  color: var(--primary-color);
  font-weight: 500;
  position: relative;
}

/* 底部蓝色指示条 */
.active-link::after {
  content: '';
  position: absolute;
  bottom: -22px; /* 调整至导航栏底部 */
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
}

.divider {
  color: var(--text-secondary);
  font-size: 12px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-regular);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--primary-light);
  border: 1px solid var(--border-color);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.main-content {
  flex: 1;
  padding: 24px;
  box-sizing: border-box;
}
</style>