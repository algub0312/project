import { useRole } from '@/composables/auth/useRole.ts'
import router from '@/router'

export async function useAfterLoginNavigation() {
  const role = useRole()
  if (role.hasRole('admin')) {
    await router.push({ name: 'admin-manage-bookings' })
  } else if (role.hasRole('user')) {
    await router.push({ name: 'book' })
  } else {
    await router.push({ name: 'unauthorized' })
  }
}
