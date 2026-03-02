<template>
  <el-container class="layout-container">
    <el-aside class="layout-aside" width="200px">
      <el-menu
        :default-active="route.path"
        :router="true"
        class="el-menu-vertical-demo"
        background-color="#1A1D2A"
        text-color="#B0B3C1"
        active-text-color="#409EFF"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header" height="60px">
        <div class="header-user">
          当前用户：<span class="header-user-name">admin</span>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { Monitor, Warning, Document, User, Edit, Key } from '@element-plus/icons-vue'

const route = useRoute()

const menuItems = [
  { path: '/dashboard', label: '仪表盘', icon: Monitor },
  { path: '/trace', label: '风险溯源', icon: Warning },
  { path: '/detect', label: '文本检测', icon: Document },
  { path: '/credit', label: '信用档案', icon: User },
  { path: '/label', label: '数据标注', icon: Edit },
  { path: '/login', label: '登录', icon: Key },
]
</script>

<style scoped>
/* 深色主题样式 */
.layout-container {
  height: 100vh;
  background-color: #0A0F1F;
}

.layout-aside {
  background-color: #1A1D2A;
  border-right: 1px solid #2A2F3A;
}

.el-menu-vertical-demo {
  background-color: #1A1D2A !important;
  border-right: none;
}

.el-menu-item {
  background-color: #1A1D2A !important;
  border-bottom: 1px solid #2A2F3A;
}

.el-menu-item:hover {
  background-color: #2A2F3A !important;
}

.el-menu-item.is-active {
  background-color: #2A2F3A !important;
  border-right: 3px solid #409EFF;
}

.layout-header {
  background-color: #1A1D2A;
  border-bottom: 1px solid #2A2F3A;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}

.header-user {
  color: #B0B3C1;
  font-size: 14px;
}

.header-user-name {
  color: #409EFF;
}

.layout-main {
  background-color: #0A0F1F;
  padding: 20px;
}
</style>