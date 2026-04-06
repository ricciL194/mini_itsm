import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    requiresAdmin?: boolean
  }
}
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false, title: '注册' }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'tickets',
        name: 'Tickets',
        component: () => import('@/views/TicketsView.vue'),
        meta: { title: '工单列表' }
      },
      {
        path: 'tickets/create',
        name: 'CreateTicket',
        component: () => import('@/views/CreateTicketView.vue'),
        meta: { title: '创建工单' }
      },
      {
        path: 'tickets/:id',
        name: 'TicketDetail',
        component: () => import('@/views/TicketDetailView.vue'),
        meta: { title: '工单详情' }
      },
      {
        path: 'tickets/:id/edit',
        name: 'TicketEdit',
        component: () => import('@/views/TicketEditView.vue'),
        meta: { title: '编辑工单' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UsersView.vue'),
        meta: { title: '用户管理', requiresAdmin: true }
      },
      {
        path: 'audit',
        name: 'Audit',
        component: () => import('@/views/AuditView.vue'),
        meta: { title: '审计日志', requiresAdmin: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { title: '个人中心' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 更新页面标题
  document.title = `${to.meta.title || 'Mini ITSM'} - 工单管理系统`

  // 需要认证的页面
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 尝试从存储恢复
      authStore.restoreFromStorage()

      if (authStore.refreshToken) {
        try {
          await authStore.doRefreshToken()
          await authStore.fetchCurrentUser()
        } catch {
          next({ name: 'Login', query: { redirect: to.fullPath } })
          return
        }
      } else {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }

    // 管理员专属页面
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      next({ name: 'Dashboard' })
      return
    }

    next()
  } else {
    // 已登录用户访问登录/注册页，跳转首页
    if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  }
})

export default router
