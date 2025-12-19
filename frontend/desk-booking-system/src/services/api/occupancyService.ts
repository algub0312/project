import apiClient from '@/services/api/client.ts'

const BASE_URL = '/occupancy/api/v1'

// Occupancy API functions
export const occupancyService = {
  // Get current occupancy status for a specific desk
  getCurrentOccupancy: async (deskId: string) => {
    const response = await apiClient.get(`${BASE_URL}/${deskId}`)
    return response.data
  },

  // Get current occupancy status for all desks
  getAllCurrentOccupancy: async () => {
    const response = await apiClient.get(`${BASE_URL}/occupancy/`)
    return response.data
  },

  // Get occupancy history for a specific desk
  getOccupancyHistory: async (
    deskId: string,
    params?: {
      limit?: number
      start_date?: string
      end_date?: string
    },
  ) => {
    const queryParams = new URLSearchParams()
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.start_date) queryParams.append('start_date', params.start_date)
    if (params?.end_date) queryParams.append('end_date', params.end_date)

    const queryString = queryParams.toString()
    const url = queryString
      ? `${BASE_URL}/occupancy/${deskId}/history?${queryString}`
      : `${BASE_URL}/occupancy/${deskId}/history`

    const response = await apiClient.get(url)
    return response.data
  },

  // Development helper - clear all occupancy records
  clearAllOccupancy: async () => {
    const response = await apiClient.delete('/occupancy/dev/')
    return response.data
  },
}
