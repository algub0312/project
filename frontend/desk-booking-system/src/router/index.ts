import LandingPageView from '@/views/LandingPageView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'landing-page',
    component: LandingPageView,
  },
  {
    path: '/book',
    name: 'book',
    component: () => import('../views/user/BookingView.vue'),
    meta: { requiresAuth: true, roles: ['user'] },
  },
  {
    path: '/my-bookings',
    name: 'my-bookings',
    component: () => import('../views/user/MyBookingsView.vue'),
    meta: { requiresAuth: true, roles: ['user'] },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/user/ProfileView.vue'),
    meta: { requiresAuth: true, roles: ['user'] },
  },
  {
    path: '/admin/bookings',
    name: 'admin-manage-bookings',
    component: () => import('../views/admin/ManageBookingsView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/desks',
    name: 'admin-manage-desks',
    component: () => import('../views/admin/ManageDesksView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/availability',
    name: 'admin-desk-availability',
    component: () => import('../views/admin/DeskAvailabilityView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/analytics',
    name: 'admin-analytics',
    component: () => import('../views/admin/AnalyticsView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/unauthorized',
    name: 'unauthorized',
    component: () => import('../views/UnauthorizedView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/PageNotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!to.meta.requiresAuth) return true
  await auth.refreshTokenIfNeeded()
  if (!auth.authenticated) return '/unauthorized'
  const requiredRoles = to.meta.roles as string[] | undefined
  if (!requiredRoles) return true
  const allowed = requiredRoles.some((r) => auth.roles.includes(r))
  if (!allowed) return '/unauthorized'
  return true
})

export default router
