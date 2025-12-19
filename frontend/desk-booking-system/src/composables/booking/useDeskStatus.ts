import { computed, type Ref } from 'vue'
import type { Desk } from '@/types/desk'
import type { Booking } from '@/types/booking'
import type { DeskStatus } from '@/types/deskStatus'

/**
 * Composable to compute desk statuses dynamically based on bookings
 *
 * This ensures the desk status always reflects the actual booking state
 * for the selected time range, rather than relying on stale data.
 */
export function useDeskStatus(
  desks: Ref<Desk[]>,
  bookings: Ref<Booking[]>,
  selectedStart: Ref<Date>,
  selectedEnd: Ref<Date>,
) {
  /**
   * Check if two time ranges overlap
   *
   * Two ranges overlap if:
   * - Range A starts before Range B ends AND
   * - Range A ends after Range B starts
   *
   * Example overlaps:
   * A: [10:00 - 12:00]
   * B: [11:00 - 13:00] ✓ overlaps
   * B: [09:00 - 10:30] ✓ overlaps
   * B: [10:00 - 12:00] ✓ overlaps (exact match)
   * B: [13:00 - 14:00] ✗ no overlap
   */
  const isBookingInRange = (booking: Booking): boolean => {
    const bookingStart = new Date(booking.startTime)
    const bookingEnd = new Date(booking.endTime)
    const rangeStart = selectedStart.value
    const rangeEnd = selectedEnd.value

    // Overlap condition: booking starts before range ends AND booking ends after range starts
    return bookingStart < rangeEnd && bookingEnd > rangeStart
  }

  /**
   * Determine the status of a desk based on current bookings
   *
   * Priority:
   * 1. If desk has maintenance status → keep it
   * 2. If desk has any overlapping bookings → occupied
   * 3. Otherwise → available
   */
  const getDeskStatus = (deskId: number): DeskStatus => {
    const desk = desks.value.find((d) => d.id === deskId)

    // Respect fixed statuses like maintenance
    if (desk?.status === 'maintenance') {
      return 'maintenance'
    }

    // Check if there are any bookings for this desk that overlap with selected time range
    const hasOverlappingBooking = bookings.value.some(
      (booking) => booking.deskId === deskId && isBookingInRange(booking),
    )

    return hasOverlappingBooking ? 'occupied' : 'available'
  }

  /**
   * Reactive computed property that returns all desks with their status
   * recalculated based on the current bookings and time range
   */
  const desksWithStatus = computed<Desk[]>(() => {
    return desks.value.map((desk) => ({
      ...desk,
      status: getDeskStatus(desk.id),
    }))
  })

  /**
   * Helper to check if a specific desk is available
   * Useful for validation before opening booking dialogs
   */
  const isDeskAvailable = (deskId: number): boolean => {
    return getDeskStatus(deskId) === 'available'
  }

  /**
   * Get all bookings for a specific desk in the selected time range
   * Useful for showing booking details or conflicts
   */
  const getDeskBookings = (deskId: number): Booking[] => {
    return bookings.value.filter(
      (booking) => booking.deskId === deskId && isBookingInRange(booking),
    )
  }

  return {
    desksWithStatus,
    getDeskStatus,
    isDeskAvailable,
    getDeskBookings,
  }
}
