import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue'),
    },
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
  ],
})

export default router
