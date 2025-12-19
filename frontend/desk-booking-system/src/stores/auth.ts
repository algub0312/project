import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getKeycloak } from '@/services/api/keycloak.ts'
import type { KeycloakTokenParsed } from 'keycloak-js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const tokenParsed = ref<KeycloakTokenParsed | null>(null)
  const authenticated = ref(false)
  const roles = ref<string[]>([])
  const refreshTimer = ref<number | null>(null)
  const refreshing = ref(false) // prevents refresh races

  const syncFromKeycloak = () => {
    const kc = getKeycloak()

    token.value = kc.token ?? null
    tokenParsed.value = kc.tokenParsed ?? null
    authenticated.value = kc.authenticated ?? false
    let clientRoles = kc.tokenParsed?.resource_access?.['vue-app']?.roles ?? []
    if (clientRoles.includes('admin')) {
      clientRoles = ['admin']
    }
    roles.value = clientRoles
  }

  const stopRefreshTimer = () => {
    if (refreshTimer.value) {
      clearTimeout(refreshTimer.value)
      refreshTimer.value = null
    }
  }

  const refreshTokenIfNeeded = async (): Promise<boolean> => {
    if (refreshing.value) return true // avoid double-refresh
    refreshing.value = true

    const kc = getKeycloak()

    try {
      const refreshed = await kc.updateToken(60)
      if (refreshed) syncFromKeycloak()
      return true
    } catch {
      await logout() // no token refresh possible, log out
      return false
    } finally {
      refreshing.value = false
    }
  }

  const scheduleRefresh = () => {
    const kc = getKeycloak()
    if (!kc.tokenParsed?.exp) return

    const exp = kc.tokenParsed.exp * 1000
    const now = Date.now()
    const refreshIn = exp - now - 60000

    const timeout = refreshIn > 0 ? refreshIn : 1000

    stopRefreshTimer()

    refreshTimer.value = window.setTimeout(async () => {
      await refreshTokenIfNeeded()
      scheduleRefresh()
    }, timeout)
  }

  const init = () => {
    syncFromKeycloak()
    scheduleRefresh()

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) refreshTokenIfNeeded()
    })

    window.addEventListener('focus', () => {
      refreshTokenIfNeeded()
    })
  }

  const login = () => getKeycloak().login()
  const editAccount = () => getKeycloak().accountManagement()
  const getProfile = () => getKeycloak().loadUserProfile()

  const logout = async () => {
    const kc = getKeycloak()

    stopRefreshTimer()

    token.value = null
    tokenParsed.value = null
    authenticated.value = false
    roles.value = []

    await kc.logout({ redirectUri: window.location.origin + '/' })
  }

  const user = computed(() => {
    if (!tokenParsed.value) return null
    const t = tokenParsed.value

    return {
      id: t.sub,
      username: t.preferred_username,
      email: t.email,
      fullName: t.name || `${t.given_name ?? ''} ${t.family_name ?? ''}`.trim(),
      firstName: t.given_name,
      lastName: t.family_name,
    }
  })

  return {
    // state
    token,
    tokenParsed,
    authenticated,
    roles,

    // actions
    init,
    login,
    logout,
    editAccount,
    getProfile,
    scheduleRefresh,

    // internals (optional)
    refreshTokenIfNeeded,
    syncFromKeycloak,

    // getters
    user,
  }
})
