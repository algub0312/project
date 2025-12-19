import { type Ref } from 'vue'
import { bookingService } from '@/services/api/bookingService.ts'
import { useAuthStore } from '@/stores/auth.ts'
import type { Desk } from '@/types/desk.ts'

export function useBookingActions(
  selectedStart: Ref<Date>,
  selectedEnd: Ref<Date>,
  selectedDesk: Ref<Desk | null>,
  bookingDialog: Ref<boolean>,
  contextMenu: Ref<boolean>,
  contextMenuDesk: Ref<Desk | null>,
) {
  const authStore = useAuthStore()

  // Open booking dialog for a desk
  const openBookingDialog = (desk: Desk) => {
    if (desk.status !== 'available') return
    selectedDesk.value = desk
    bookingDialog.value = true
  }

  // Handle right-click context menu
  const handleDeskRightClick = (desk: Desk, ev: MouseEvent) => {
    ev.preventDefault()
    if (desk.status !== 'available') return
    contextMenuDesk.value = desk
    contextMenu.value = true
  }

  // Quick booking actions
  const quickBookNow = (desk: Desk, durationHours: number) => {
    const now = new Date()
    now.setMinutes(0, 0, 0)
    selectedStart.value = now
    selectedEnd.value = new Date(now.getTime() + durationHours * 60 * 60 * 1000)
    selectedDesk.value = desk
    contextMenu.value = false
    bookingDialog.value = true
  }

  const bookHalfDay = (desk: Desk) => {
    const today = new Date()
    today.setHours(9, 0, 0, 0)
    selectedStart.value = today
    const end = new Date(today)
    end.setHours(13, 0, 0, 0)
    selectedEnd.value = end
    selectedDesk.value = desk
    contextMenu.value = false
    bookingDialog.value = true
  }

  const bookFullDay = (desk: Desk) => {
    const today = new Date()
    today.setHours(9, 0, 0, 0)
    selectedStart.value = today
    const end = new Date(today)
    end.setHours(17, 0, 0, 0)
    selectedEnd.value = end
    selectedDesk.value = desk
    contextMenu.value = false
    bookingDialog.value = true
  }

  // Create booking
  const createBooking = async () => {
    if (!selectedDesk.value || !authStore.user?.id) {
      console.error('Missing desk or user')
      return
    }

    const bookingData = {
      userId: authStore.user.id,
      deskId: selectedDesk.value.id,
      startTime: selectedStart.value.toISOString(),
      endTime: selectedEnd.value.toISOString(),
    }

    try {
      console.log('Creating booking:', bookingData)
      const response = await bookingService.create(bookingData)
      console.log('Booking created successfully:', response)
      bookingDialog.value = false
      selectedDesk.value = null
      return response
    } catch (error) {
      console.error('Error creating booking:', error)
      throw error
    }
  }

  return {
    openBookingDialog,
    handleDeskRightClick,
    quickBookNow,
    bookHalfDay,
    bookFullDay,
    createBooking,
  }
}
