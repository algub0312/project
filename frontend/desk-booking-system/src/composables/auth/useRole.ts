import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.ts'

export function useRole() {
  const auth = useAuthStore()

  const isAuthenticated = computed(() => auth.authenticated)

  const hasRole = (role: string) => {
    return auth.roles.includes(role)
  }

  const hasAnyRole = (...roles: string[]) => {
    return roles.some((r) => auth.roles.includes(r))
  }

  const hasAllRoles = (...roles: string[]) => {
    return roles.every((r) => auth.roles.includes(r))
  }

  return {
    isAuthenticated,
    hasRole,
    hasAnyRole,
    hasAllRoles,
  }
}
