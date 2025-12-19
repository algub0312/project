import { ref, type Ref } from 'vue'
import type { Booking } from '@/types/mockData'
import { todayISO } from '@/utils/datetime'
import { bookingService } from '@/services/api/bookingService.ts'
import { useAuthStore } from '@/stores/auth.ts'
import type { Desk } from '@/types/desk.ts'

export function useBookingLogic(
  desks: Ref<Desk[]>,
  userBookings: Ref<Booking[]>,
  CURRENT_USER: string,
) {
  // dialogs
  const contextMenu = ref(false)
  const contextMenuDesk = ref<Desk | null>(null)

  const bookingDialog = ref(false)
  const selectedDesk = ref<Desk | null>(null)
  const bookingDate = ref(todayISO())
  const startTime = ref('09:00')
  const endTime = ref('17:00')

  const weeklyAvailabilityDialog = ref(false)
  const selectedDeskForWeekly = ref<Desk>()

  // colors
  const getDeskColor = (status: string): string => {
    switch (status) {
      case 'available':
        return '#4caf50' // green
      case 'occupied':
        return '#f44336' // red
      case 'reserved':
        return '#ff9800' // orange
      default:
        return '#9e9e9e' // grey
    }
  }

  // click / context
  const handleDeskClick = (desk: Desk) => {
    if (desk.status !== 'available') return
    selectedDesk.value = desk
    bookingDate.value = todayISO()
    startTime.value = '09:00'
    endTime.value = '17:00'
    bookingDialog.value = true
  }
  const handleDeskRightClick = (desk: Desk, ev: MouseEvent) => {
    ev.preventDefault()
    if (desk.status !== 'available') return
    contextMenuDesk.value = desk
    contextMenu.value = true
  }

  // quick actions right click
  const quickBook = (desk: Desk, hours: number) => {
    const now = new Date()
    const hh = String(now.getHours()).padStart(2, '0')
    const mm = String(now.getMinutes()).padStart(2, '0')
    selectedDesk.value = desk
    bookingDate.value = todayISO()
    startTime.value = `${hh}:${mm}`
    endTime.value = `${String(now.getHours() + hours).padStart(2, '0')}:${mm}`
    contextMenu.value = false
    bookingDialog.value = true
  }
  const bookHalfDay = (desk: Desk) => {
    selectedDesk.value = desk
    bookingDate.value = todayISO()
    startTime.value = '09:00'
    endTime.value = '13:00'
    contextMenu.value = false
    bookingDialog.value = true
  }
  const bookFullDay = (desk: Desk) => {
    selectedDesk.value = desk
    bookingDate.value = todayISO()
    startTime.value = '09:00'
    endTime.value = '17:00'
    contextMenu.value = false
    bookingDialog.value = true
  }

  // favorite
  const toggleFavorite = (desk: Desk) => {
    const idx = desks.value.findIndex((d: Desk) => d.id === desk.id)
    if (idx !== -1) desks.value[idx].isFavorite = !desks.value[idx].isFavorite
    contextMenu.value = false
  }

  // confirm / cancel
  const confirmBooking = () => {
    if (!selectedDesk.value || !bookingDate.value || !startTime.value || !endTime.value) return

    const authStore = useAuthStore()
    if (!authStore.user) {
      console.error('No authenticated user found')
      return
    }
    const bookingData = {
      userId: authStore.user.id!,
      deskId: selectedDesk.value.id,
      startTime: new Date(`${bookingDate.value}T${startTime.value}:00`).toISOString(),
      endTime: new Date(`${bookingDate.value}T${endTime.value}:00`).toISOString(),
    }
    console.log('Creating booking:', bookingData)
    bookingService
      .create(bookingData)
      .then((response) => {
        console.log('Booking API response:', response)
      })
      .catch((error) => {
        console.error('Error creating booking:', error)
        console.error(error.response?.data)
      })
    console.log('Booking created successfully')
    const newBooking: Booking = {
      id: String(userBookings.value.length + 1),
      deskId: selectedDesk.value.id,
      date: bookingDate.value,
      startTime: startTime.value,
      endTime: endTime.value,
      userId: CURRENT_USER,
      status: 'active',
      createdAt: new Date().toISOString(),
    }
    userBookings.value.push(newBooking)

    const i = desks.value.findIndex((d: Desk) => d.id === selectedDesk.value?.id)
    if (i !== -1) {
      desks.value[i].status = 'reserved'
      desks.value[i].bookedBy = CURRENT_USER
    }
    bookingDialog.value = false
    selectedDesk.value = null
  }
  const cancelBooking = () => {
    bookingDialog.value = false
    selectedDesk.value = null
  }

  // weekly availability
  const viewWeeklyAvailability = (desk: Desk) => {
    selectedDeskForWeekly.value = desk
    weeklyAvailabilityDialog.value = true
    contextMenu.value = false
  }

  return {
    // state
    contextMenu,
    contextMenuDesk,
    bookingDialog,
    selectedDesk,
    bookingDate,
    startTime,
    endTime,
    weeklyAvailabilityDialog,
    selectedDeskForWeekly,
    // actions
    getDeskColor,
    handleDeskClick,
    handleDeskRightClick,
    quickBook,
    bookHalfDay,
    bookFullDay,
    toggleFavorite,
    confirmBooking,
    cancelBooking,
    viewWeeklyAvailability,
  }
}
