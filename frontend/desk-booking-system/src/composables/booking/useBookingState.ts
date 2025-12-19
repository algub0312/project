import { ref, computed } from 'vue'

import type { Desk } from '@/types/desk.ts'

export function useBookingState() {
  // Time selection state (single source of truth)
  const selectedStart = ref<Date>(new Date())
  selectedStart.value.setMinutes(0, 0, 0)
  const selectedEnd = ref<Date>(new Date(new Date().getTime() + 60 * 60 * 1000))
  selectedEnd.value.setMinutes(0, 0, 0)

  // Dialog states
  const bookingDialog = ref(false)
  const selectedDesk = ref<Desk | null>(null)
  const contextMenu = ref(false)
  const contextMenuDesk = ref<Desk | null>(null)
  const weeklyAvailabilityDialog = ref(false)
  const selectedDeskForWeekly = ref<Desk>()

  // Computed formatting
  const formattedDateRange = computed(() => {
    const dateStr = selectedStart.value.toLocaleDateString(undefined, {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
    const startTime = selectedStart.value.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
    const endTime = selectedEnd.value.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
    return { dateStr, startTime, endTime }
  })

  return {
    // Time state
    selectedStart,
    selectedEnd,
    formattedDateRange,

    // Dialog states
    bookingDialog,
    selectedDesk,
    contextMenu,
    contextMenuDesk,
    weeklyAvailabilityDialog,
    selectedDeskForWeekly,
  }
}
