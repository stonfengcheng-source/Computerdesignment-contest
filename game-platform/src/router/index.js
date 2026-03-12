import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // --- 独立全屏视图 ---
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingView.vue'), // 刚才创建的气泡展示页
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue'),
    },

    // --- 包含系统导航栏/侧边栏的业务视图 ---
    {
      path: '/systemRoot', // 虚拟根节点，用于挂载 Layout
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