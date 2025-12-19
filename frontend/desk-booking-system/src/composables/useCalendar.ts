import { computed, type Ref } from 'vue'
import type { Booking } from '@/types/mockData'
import { getWeekDays, hoursBetween } from '@/utils/datetime'

export function useCalendar(userBookings: Ref<Booking[]>) {
  const weekDays = computed(() => getWeekDays())

  const bookingsForDay = (isoDate: string) =>
    userBookings.value.filter((b: Booking) => b.date === isoDate)

  const getDeskBookingForDate = (deskId: number, date: string) =>
    userBookings.value.find((b: Booking) => b.deskId === deskId && b.date === date)

  return { weekDays, bookingsForDay, getDeskBookingForDate, hoursBetween }
}
