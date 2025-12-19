import { useAuthStore } from '@/stores/auth'
import { useAfterLoginNavigation } from '@/composables/auth/useNavigation.ts'

export async function handleLoginRedirect() {
  const auth = useAuthStore()
  auth.syncFromKeycloak()
  auth.scheduleRefresh()
  await useAfterLoginNavigation()
}
