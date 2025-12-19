import apiClient from '@/services/api/client.ts'

const BASE_URL = '/desk-integration/api/v1'

// Only TEMPORARY, to be replaced with the Desk Inventory Service later
export const deskIntegrationService = {
  // Get all desks
  getAllDesks: async () => {
    const response = await apiClient.get(`${BASE_URL}/desks`)
    return response.data
  },

  // Get specific desk by ID
  getDesk: async (deskId: number) => {
    const response = await apiClient.get(`${BASE_URL}/desks/${deskId}`)
    return response.data
  },

  // Get desk configuration
  getDeskConfig: async (deskId: number) => {
    const response = await apiClient.get(`${BASE_URL}/desks/${deskId}/config`)
    return response.data
  },

  // Get desk state
  getDeskState: async (deskId: number) => {
    const response = await apiClient.get(`${BASE_URL}/desks/${deskId}/state`)
    return response.data
  },

  // Set desk height
  setDeskHeight: async (deskId: number, positionMm: number) => {
    const response = await apiClient.put(`${BASE_URL}/desks/${deskId}/state`, null, {
      params: { position_mm: positionMm },
    })
    return response.data
  },

  // Get desk usage
  getDeskUsage: async (deskId: number) => {
    const response = await apiClient.get(`${BASE_URL}/desks/${deskId}/usage`)
    return response.data
  },

  // Get desk errors
  getDeskErrors: async (deskId: number) => {
    const response = await apiClient.get(`${BASE_URL}/desks/${deskId}/errors`)
    return response.data
  },
}
