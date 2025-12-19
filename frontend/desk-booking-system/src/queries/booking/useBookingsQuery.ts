import { useQuery } from '@tanstack/vue-query'
import { bookingService } from '@/services/api/bookingService.ts'
import type { Booking } from '@/types/booking.ts'
import { computed, type Ref } from 'vue'

export function useBookingsQuery(start: Ref<Date>, end: Ref<Date>) {
  return useQuery<Booking[]>({
    queryKey: ['bookings', start, end],
    queryFn: () =>
      bookingService.getByTimeRange(start.value.toISOString(), end.value.toISOString()),
    enabled: computed(() => !!start.value && !!end.value),
    staleTime: 1000 * 60, // 1 minute
  })
}
