import apiClient from '@/services/api/client.ts'
import type { DeskPreferences } from '@/types/deskPreferences.ts'
import type { UserResponse } from '@/types/user/userResponse.ts'
import { toCamelCase, toSnakeCase } from '@/services/api/util.ts'
import type { UserUpdateRequest } from '@/types/user/userUpdateRequest.ts'

const BASE_URL = '/user/api/v1'

// User API functions
export const userService = {
  // Get user profile information
  getUserById: async (userId: string): Promise<UserResponse> => {
    const response = await apiClient.get(`${BASE_URL}/users/${userId}`)
    return toCamelCase(response.data)
  },

  // Update user profile information
  updateDeskPreferences: async (
    userId: string,
    userHeight: number,
    preferences: DeskPreferences,
  ) => {
    const updateRequest: UserUpdateRequest = {
      preferredStandingHeightCm: preferences.standingHeight,
      preferredSittingHeightCm: preferences.sittingHeight,
      userHeightCm: userHeight,
    }
    const body = { ...toSnakeCase(updateRequest) }
    const response = await apiClient.put(`${BASE_URL}/users/${userId}`, body)
    return response.data
  },

  // Get all users
  getAllUsers: async (): Promise<UserResponse[]> => {
    const response = await apiClient.get(`${BASE_URL}/users/`)
    return response.data
  },
}
