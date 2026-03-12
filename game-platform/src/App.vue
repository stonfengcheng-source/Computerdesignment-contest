<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
// 这里留出空间，后续你可以按自己的自定义语法习惯引入全局的配置或状态
</script>

<style>
/* 确保挂载点撑满全屏，无默认边距干扰物理气泡边界 */
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
}
</style>