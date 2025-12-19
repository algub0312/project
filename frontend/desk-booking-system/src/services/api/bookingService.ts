import apiClient from '@/services/api/client.ts'
import { toCamelCase, toSnakeCase } from '@/services/api/util.ts'
import type { Booking } from '@/types/booking.ts'

const BASE_URL = '/booking/api/v1/bookings'

export const bookingService = {
  /**
   * Get bookings within a specific time range
   * @param start ISO string of start time
   * @param end ISO string of end time
   */
  getByTimeRange: async (start: string, end: string): Promise<Booking[]> => {
    console.log(`Fetching bookings from ${start} to ${end}`)
    const res = await apiClient.get(`${BASE_URL}?start=${start}&end=${end}`)
    return toCamelCase(res.data)
  },
  getById: (id: string) => apiClient.get(`${BASE_URL}/${id}`).then((res) => res.data),
  /**
   * Create a new booking
   * @param data Booking data with startTime and endTime as ISO strings
   */
  create: (data: { userId: string; deskId: number; startTime: string; endTime: string }) =>
    apiClient.post(BASE_URL, toSnakeCase(data)).then((res) => res.data),
  update: (
    id: string,
    data: {
      userId?: string
      startTime?: string
      endTime?: string
    },
  ) => apiClient.put(`${BASE_URL}/${id}`, toSnakeCase(data)).then((res) => res.data),
  delete: (id: string) => apiClient.delete(`${BASE_URL}/${id}`).then((res) => res.data),
}
