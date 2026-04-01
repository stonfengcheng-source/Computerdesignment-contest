// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        { path: '', name: 'intro', component: () => import('../views/LandingView.vue'), meta: { title: '介绍导入' } },
        { path: 'dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue'), meta: { title: '总览台' } },
        { path: 'detect', name: 'detect', component: () => import('../views/TextDetectionView.vue'), meta: { title: '多模态毒性检测' } }, // <--- 就是这里漏了逗号！
        { path: 'monitor', name: 'monitor', component: () => import('../views/MonitorView.vue'), meta: { title: '实时监测' } },
        { path: 'trace', name: 'trace', component: () => import('../views/RiskTraceView.vue'), meta: { title: '风险溯源拓扑' } },
        { path: 'label', name: 'label', component: () => import('../views/DataLabelingView.vue'), meta: { title: '对抗数据标注' } }
      ]
    }
  ]
})
export default router