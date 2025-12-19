// composables/useBookingsAdmin.ts
import { ref, reactive, computed, onMounted } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import { mockBookings, mockUsers, mockDesks } from '@/types/mockData'
import type { Booking } from '@/types/mockData'
import {
  filterBookings,
  enrichBooking,
  normalizeStatus,
  type BookingDisplay,
  type BookingFilters,
} from '@/utils/bookingAdminHelpers'

type SnackbarColor = 'success' | 'warning' | 'error' | 'info'

interface DialogState {
  details: boolean
  edit: boolean
  cancel: boolean
  delete: boolean
}

interface SnackbarState {
  show: boolean
  text: string
  color: SnackbarColor
}

interface UseBookingAdminReturn {
  bookings: Ref<BookingDisplay[]>
  loading: Ref<boolean>
  filteredBookings: ComputedRef<BookingDisplay[]>
  filters: BookingFilters
  dialogs: DialogState
  selectedBooking: Ref<BookingDisplay | null>
  editingBooking: Ref<BookingDisplay | null>
  snackbar: SnackbarState
  resetFilters: () => void
  handleView: (booking: BookingDisplay) => void
  handleEdit: (booking: BookingDisplay) => void
  handleSave: (updatedBooking: BookingDisplay) => void
  handleCancel: (booking: BookingDisplay) => void
  confirmCancel: () => void
  handleDelete: (booking: BookingDisplay) => void
  confirmDelete: () => void
}

export function useBookingsAdmin(): UseBookingAdminReturn {
  const rawBookings = ref<Booking[]>(JSON.parse(JSON.stringify(mockBookings)))
  const bookings = ref<BookingDisplay[]>([])
  const loading = ref<boolean>(false)

  // Filters
  const filters = reactive<BookingFilters>({
    search: '',
    status: 'All',
    dateRange: 'All',
    customDate: '',
  })

  // Dialogs
  const dialogs = reactive<DialogState>({
    details: false,
    edit: false,
    cancel: false,
    delete: false,
  })

  // Selected items
  const selectedBooking = ref<BookingDisplay | null>(null)
  const editingBooking = ref<BookingDisplay | null>(null)
  const bookingToCancel = ref<BookingDisplay | null>(null)
  const bookingToDelete = ref<BookingDisplay | null>(null)

  // Snackbar
  const snackbar = reactive<SnackbarState>({
    show: false,
    text: '',
    color: 'success',
  })

  // Filtered bookings
  const filteredBookings = computed<BookingDisplay[]>(() => {
    return filterBookings(bookings.value, filters)
  })

  // Enrich bookings user and desk info
  const enrichAllBookings = (): void => {
    bookings.value = rawBookings.value.map((booking) =>
      enrichBooking(booking, mockUsers, mockDesks),
    )
  }

  // Fetch bookings
  const fetchBookings = async (): Promise<void> => {
    loading.value = true

    await new Promise((resolve) => setTimeout(resolve, 500))

    // Enrich bookings
    enrichAllBookings()

    loading.value = false
  }

  // Reset filters
  const resetFilters = (): void => {
    filters.search = ''
    filters.status = 'All'
    filters.dateRange = 'All'
    filters.customDate = ''
  }

  // Show snackbar
  const showSnackbar = (text: string, color: SnackbarColor): void => {
    snackbar.text = text
    snackbar.color = color
    snackbar.show = true
  }

  // View booking details
  const handleView = (booking: BookingDisplay): void => {
    selectedBooking.value = booking
    dialogs.details = true
  }

  // Edit booking
  const handleEdit = (booking: BookingDisplay): void => {
    editingBooking.value = { ...booking }
    dialogs.edit = true
  }

  // Save edited booking
  const handleSave = (updatedBooking: BookingDisplay): void => {
    const index = rawBookings.value.findIndex((b) => b.id === updatedBooking.id)
    if (index !== -1) {
      // Update raw booking
      rawBookings.value[index] = {
        ...rawBookings.value[index],
        date: updatedBooking.date,
        startTime: updatedBooking.startTime,
        endTime: updatedBooking.endTime,
        status: updatedBooking.status,
        notes: updatedBooking.notes,
      }

      // Re-enrich bookings
      enrichAllBookings()

      showSnackbar('Booking updated successfully', 'success')
    }
    dialogs.edit = false
  }

  // Cancel booking
  const handleCancel = (booking: BookingDisplay): void => {
    bookingToCancel.value = booking
    dialogs.cancel = true
  }

  // Confirm cancel
  const confirmCancel = (): void => {
    if (!bookingToCancel.value) return

    const index = rawBookings.value.findIndex((b) => b.id === bookingToCancel.value!.id)
    if (index !== -1) {
      rawBookings.value[index].status = 'cancelled'
      enrichAllBookings()
      showSnackbar('Booking cancelled successfully', 'warning')
    }
    dialogs.cancel = false
    bookingToCancel.value = null
  }

  // Delete booking
  const handleDelete = (booking: BookingDisplay): void => {
    bookingToDelete.value = booking
    dialogs.delete = true
  }

  // Confirm delete
  const confirmDelete = (): void => {
    if (!bookingToDelete.value) return

    const index = rawBookings.value.findIndex((b) => b.id === bookingToDelete.value!.id)
    if (index !== -1) {
      rawBookings.value.splice(index, 1)
      enrichAllBookings()
      showSnackbar('Booking deleted successfully', 'error')
    }
    dialogs.delete = false
    bookingToDelete.value = null
  }

  // Fetch on mount
  onMounted(() => {
    fetchBookings()
  })

  return {
    bookings,
    loading,
    filteredBookings,
    filters,
    dialogs,
    selectedBooking,
    editingBooking,
    snackbar,
    resetFilters,
    handleView,
    handleEdit,
    handleSave,
    handleCancel,
    confirmCancel,
    handleDelete,
    confirmDelete,
  }
}
