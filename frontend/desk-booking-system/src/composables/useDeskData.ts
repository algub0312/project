import { ref, computed } from 'vue'
import { mockDesks, mockBookings, type Booking } from '@/types/mockData'
import { hoursBetween, getWeekBounds } from '@/utils/datetime'
import type { Desk } from '@/types/desk.ts'

const CURRENT_USER = 'current-user'

export function useDeskData() {
  const desks = ref<Desk[]>(JSON.parse(JSON.stringify(mockDesks)))
  const userBookings = ref<Booking[]>(JSON.parse(JSON.stringify(mockBookings)))

  // Stats (week/month)
  const hoursThisWeek = computed(() => {
    const { start, end } = getWeekBounds(new Date())
    return userBookings.value
      .filter((b) => {
        const d = new Date(b.date)
        return d >= start && d <= end
      })
      .reduce((sum, b) => sum + hoursBetween(b.startTime, b.endTime), 0)
  })

  const hoursThisMonth = computed(() => {
    const now = new Date()
    const m = now.getMonth(),
      y = now.getFullYear()
    return userBookings.value
      .filter((b) => {
        const d = new Date(b.date)
        return d.getMonth() === m && d.getFullYear() === y
      })
      .reduce((sum, b) => sum + hoursBetween(b.startTime, b.endTime), 0)
  })

  return { CURRENT_USER, desks, userBookings, hoursThisWeek, hoursThisMonth }
}
