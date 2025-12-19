import type { Booking as MockBooking, User } from '@/types/mockData'
import type { Desk } from '@/types/desk.ts'

export interface BookingDisplay extends MockBooking {
  userName: string
  userEmail: string
  deskName: number
  floor: number
  timeSlot: string
}

export interface BookingFilters {
  search: string
  status: string
  dateRange: string
  customDate: string
}

export type StatusColor = 'success' | 'info' | 'error' | 'grey'
export type DateRangeOption = 'All' | 'Today' | 'This Week' | 'This Month' | 'Past' | 'Future'

export const enrichBooking = (
  booking: MockBooking,
  users: User[],
  desks: Desk[],
): BookingDisplay => {
  const user = users.find((u) => u.id === booking.userId)
  const desk = desks.find((d) => d.id === booking.deskId)

  return {
    ...booking,
    userName: user?.username || 'Unknown User',
    userEmail: user?.email || '',
    deskName: desk?.id || booking.deskId,
    floor: desk?.floor || 1,
    timeSlot: `${booking.startTime}-${booking.endTime}`,
  }
}

export const normalizeStatus = (status: string): 'Active' | 'Completed' | 'Cancelled' => {
  const statusMap: Record<string, 'Active' | 'Completed' | 'Cancelled'> = {
    active: 'Active',
    completed: 'Completed',
    cancelled: 'Cancelled',
  }
  return statusMap[status.toLowerCase()] || 'Active'
}

export const getUserInitials = (name: string): string => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ro-RO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ro-RO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const getStatusColor = (status: string): StatusColor => {
  const normalizedStatus = normalizeStatus(status)
  const colors: Record<'Active' | 'Completed' | 'Cancelled', StatusColor> = {
    Active: 'success',
    Completed: 'info',
    Cancelled: 'error',
  }
  return colors[normalizedStatus] || 'grey'
}

export const filterBookings = (
  bookings: BookingDisplay[],
  filters: BookingFilters,
): BookingDisplay[] => {
  let filtered = bookings

  // Search filter
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(
      (b) =>
        b.userName.toLowerCase().includes(searchLower) ||
        b.userEmail.toLowerCase().includes(searchLower) ||
        b.deskName.toString().includes(searchLower),
    )
  }

  // Status filter
  if (filters.status !== 'All') {
    filtered = filtered.filter((b) => normalizeStatus(b.status) === filters.status)
  }

  // Date range filter
  if (filters.dateRange !== 'All') {
    filtered = filterByDateRange(filtered, filters.dateRange as DateRangeOption)
  }

  // Custom date filter
  if (filters.customDate) {
    filtered = filtered.filter((b) => b.date === filters.customDate)
  }

  return filtered
}

const filterByDateRange = (
  bookings: BookingDisplay[],
  dateRange: DateRangeOption,
): BookingDisplay[] => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  return bookings.filter((b) => {
    const bookingDate = new Date(b.date)
    bookingDate.setHours(0, 0, 0, 0)

    switch (dateRange) {
      case 'Today':
        return bookingDate.getTime() === today.getTime()

      case 'This Week': {
        const weekStart = new Date(today)
        weekStart.setDate(today.getDate() - today.getDay())

        const weekEnd = new Date(weekStart)
        weekEnd.setDate(weekStart.getDate() + 6)

        return bookingDate >= weekStart && bookingDate <= weekEnd
      }

      case 'This Month':
        return (
          bookingDate.getMonth() === today.getMonth() &&
          bookingDate.getFullYear() === today.getFullYear()
        )

      case 'Past':
        return bookingDate < today

      case 'Future':
        return bookingDate > today

      case 'All':
      default:
        return true
    }
  })
}
