import { createRouter, createWebHistory } from 'vue-router'
import TextDetectionView from '@/views/TextDetectionView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // --- 独立全屏视图 ---
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue'),
    },

    // --- 包含系统导航栏/侧边栏的业务视图 ---
    {
      path: '/systemRoot',
      component: () => import('../views/Layout.vue'),
      children: [
        {
          path: '/dashboard',
          name: 'dashboard',
          component: () => import('../views/Dashboard.vue'),
        },
        {
          path: '/trace',
          name: 'trace',
          component: () => import('../views/Trace.vue'),
        },
        {
          path: '/detect',
          name: 'detect',
          component: () => import('../views/Detect.vue'),
        },
        {
          path: '/credit',
          name: 'credit',
          component: () => import('../views/Credit.vue'),
        },
        {
          path: '/label',
          name: 'label',
          component: () => import('../views/Label.vue'),
        },
        // 👇 就是这里！确保它 import 的是 Behavior.vue，而不是 Dashboard.vue
        {
          path: '/behavior',
          name: 'behavior',
          component: () => import('../views/Behavior.vue'),
        },
        {
          path: '/text-detection',
          name: 'TextDetection',
          component: TextDetectionView
        },
        {
          path: '/about',
          name: 'about',
          component: () => import('../views/AboutView.vue'),
        }
      ]
    }
  ],
})

export default router