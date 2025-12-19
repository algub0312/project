import apiClient from '@/services/api/client.ts'

const BASE_URL = 'scheduler/scheduler/api/v1'

// Scheduler API functions
export const schedulerService = {
  // Set all desks to a specific position
  setAllDesksPosition: async (positionMm: number) => {
    const response = await apiClient.post(`${BASE_URL}/desks/position`, {
      position_mm: positionMm,
    })
    return response.data
  },

  // Schedule management
  createSchedule: async (schedule: {
    name: string
    position_mm: number
    cron: {
      hour: number
      minute: number
      day_of_week: string
    }
    id?: string
  }) => {
    const response = await apiClient.post(`${BASE_URL}/schedules`, schedule)
    return response.data
  },

  getSchedules: async () => {
    const response = await apiClient.get(`${BASE_URL}/schedules`)
    return response.data
  },

  deleteSchedule: async (jobId: string) => {
    const response = await apiClient.delete(`${BASE_URL}/schedules/${jobId}`)
    return response.data
  },
}
