<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="logo-zone">
        <div class="logo-icon"></div>
        <h2>Deep Blue</h2>
      </div>

      <nav class="menu-container">
        <div
          v-for="(item, index) in activeMenu"
          :key="index"
          class="menu-item"
          :class="{ 'is-active': currentPath === item.route }"
          @click="navigate(item.route)"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="text">{{ item.label }}</span>
        </div>
      </nav>
    </aside>

    <main class="main-wrapper">
      <header class="top-header">
        <div class="breadcrumb">
          <span class="text-gray">系统矩阵 / </span>
          <span class="text-blue">{{ currentMenuName }}</span>
        </div>
        <div class="user-actions">
          <div class="admin-badge">Admin</div>
          <button class="logout-btn" @click="doLogout">退出系统</button>
        </div>
      </header>

      <div class="content-body">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

// 原始菜单配置
const rawMenuData = [
  { route: '/dashboard', label: '控制台总览', icon: '📊' },
  { route: '/trace', label: '风险溯源拓扑', icon: '🕸️' },
  { route: '/credit', label: '跨平台信用评级', icon: '🛡️' },
  { route: '/detect', label: '多模态毒性检测', icon: '🎭' },
  { route: '/label', label: '对抗数据标注', icon: '🏷️' }
];

// 采用 while 循环结构对菜单进行装载处理
const activeMenu = ref([]);
let i = 0;
while (i < rawMenuData.length) {
  activeMenu.value.push(rawMenuData[i]);
  i++;
}

const currentPath = computed(() => route.path);
const currentMenuName = computed(() => {
  let j = 0;
  while (j < activeMenu.value.length) {
    if (activeMenu.value[j].route === currentPath.value) {
      return activeMenu.value[j].label;
    }
    j++;
  }
  return '功能模块';
});

const navigate = (path) => {
  if (currentPath.value !== path) {
    router.push(path);
  }
};

const doLogout = () => {
  // 退出回到气泡展示页
  router.push('/');
};
</script>

<style scoped>
.app-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: #f1f5f9; /* 极浅冷灰底色 */
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

/* 侧边栏样式 */
.sidebar {
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02);
  z-index: 10;
}

.logo-zone {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #f1f5f9;
}

.logo-icon {
  width: 12px;
  height: 12px;
  background: #0ea5e9;
  border-radius: 50%;
  box-shadow: 0 0 10px #0ea5e9;
  margin-right: 12px;
}

.logo-zone h2 {
  font-size: 1.4rem;
  font-weight: 900;
  color: #0f172a;
  margin: 0;
}

.menu-container {
  padding: 24px 16px;
  flex: 1;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  margin-bottom: 8px;
  border-radius: 12px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.menu-item:hover {
  background: #f8fafc;
  color: #0f172a;
}

.menu-item.is-active {
  background: #e0f2fe;
  color: #0284c7;
  font-weight: 700;
}

.menu-item .icon {
  font-size: 1.2rem;
  margin-right: 12px;
}

/* 主内容区 */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  height: 80px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.breadcrumb .text-gray {
  color: #94a3b8;
}
.breadcrumb .text-blue {
  color: #0ea5e9;
  font-weight: 600;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.admin-badge {
  background: #f1f5f9;
  padding: 6px 16px;
  border-radius: 20px;
  color: #334155;
  font-weight: 600;
  font-size: 0.9rem;
}

.logout-btn {
  background: transparent;
  border: 1px solid #cbd5e1;
  padding: 6px 16px;
  border-radius: 20px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

.content-body {
  flex: 1;
  overflow-y: auto;
  position: relative;
  /* 内边距在子组件中控制，这里保持全屏 */
}

/* 路由切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>