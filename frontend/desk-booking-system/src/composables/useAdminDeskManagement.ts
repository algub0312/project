import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import type { Booking } from '@/types/mockData'
import type { Desk } from '@/types/desk.ts'
import type { DeskStatus } from '@/types/deskStatus.ts'

export function useAdminDeskManagement(desks: Ref<Desk[]>, bookings: Ref<Booking[]>) {
  /* Floor Selection */
  const selectedFloor = ref(0)

  /* Status Filter */
  const statusFilter = ref<DeskStatus | 'all'>('all')

  /* Management Dialog */
  const managementDialog = ref(false)
  const selectedDesk = ref<Desk | null>(null)

  /* Filtered Desks by Floor */
  const desksByFloor = computed(() => {
    let filtered = desks.value.filter((desk) => desk.floor === selectedFloor.value)

    if (statusFilter.value !== 'all') {
      filtered = filtered.filter((desk) => desk.status === statusFilter.value)
    }

    return filtered
  })

  /* Statistics */
  const stats = computed(() => {
    const floorDesks = desks.value.filter((d) => d.floor === selectedFloor.value)
    return {
      total: floorDesks.length,
      available: floorDesks.filter((d) => d.status === 'available').length,
      occupied: floorDesks.filter((d) => d.status === 'occupied').length,
      reserved: floorDesks.filter((d) => d.status === 'reserved').length,
      maintenance: floorDesks.filter((d) => d.status === 'maintenance').length,
    }
  })

  /* Get Desk Color */
  const getDeskColor = (status: DeskStatus) => {
    switch (status) {
      case 'available':
        return 'success'
      case 'occupied':
        return 'error'
      case 'reserved':
        return 'warning'
      case 'maintenance':
        return 'grey'
      default:
        return 'grey'
    }
  }

  /* Handle Desk Click */
  const handleDeskClick = (desk: Desk) => {
    selectedDesk.value = desk
    managementDialog.value = true
  }

  /* Handle Right Click */
  const handleDeskRightClick = (event: MouseEvent, desk: Desk) => {
    event.preventDefault()
    handleDeskClick(desk)
  }

  /* Update Desk Status */
  const updateDeskStatus = (deskId: number, status: DeskStatus) => {
    const deskIndex = desks.value.findIndex((d) => d.id === deskId)
    if (deskIndex !== -1) {
      desks.value[deskIndex].status = status

      if (status === 'maintenance' || status === 'available') {
        desks.value[deskIndex].bookedBy = undefined
      }
    }
  }

  /* Update Booking */
  const updateBooking = (booking: Booking) => {
    const bookingIndex = bookings.value.findIndex((b) => b.id === booking.id)
    if (bookingIndex !== -1) {
      bookings.value[bookingIndex] = booking
    }
  }

  /* Delete Booking */
  const deleteBooking = (bookingId: string) => {
    const bookingIndex = bookings.value.findIndex((b) => b.id === bookingId)
    if (bookingIndex !== -1) {
      const booking = bookings.value[bookingIndex]
      bookings.value.splice(bookingIndex, 1)

      // Update desk status if no more bookings
      const deskHasMoreBookings = bookings.value.some(
        (b) => b.deskId === booking.deskId && b.status === 'active',
      )
      if (!deskHasMoreBookings) {
        const deskIndex = desks.value.findIndex((d) => d.id === booking.deskId)
        if (deskIndex !== -1) {
          desks.value[deskIndex].status = 'available'
          desks.value[deskIndex].bookedBy = undefined
        }
      }
    }
  }

  return {
    selectedFloor,
    statusFilter,
    desksByFloor,
    stats,
    managementDialog,
    selectedDesk,
    getDeskColor,
    handleDeskClick,
    handleDeskRightClick,
    updateDeskStatus,
    updateBooking,
    deleteBooking,
  }
}
