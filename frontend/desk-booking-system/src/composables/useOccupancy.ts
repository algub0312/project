// src/composables/useOccupancy.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { occupancyService } from '@/services/api/occupancyService.ts'

export interface OccupancyStatus {
  desk_id: number
  occupied: boolean
  last_updated: string
  sensor_id?: string
}

export function useOccupancy(autoRefresh = true, refreshInterval = 30000) {
  const occupancyStatuses = ref<OccupancyStatus[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const intervalId = ref<number | null>(null)

  const fetchAllOccupancy = async () => {
    isLoading.value = true
    error.value = null

    try {
      const data = await occupancyService.getAllCurrentOccupancy()
      occupancyStatuses.value = data
      return data
    } catch (err) {
      console.error('Error fetching occupancy:', err)
      error.value = 'Failed to load occupancy status'
      return []
    } finally {
      isLoading.value = false
    }
  }

  const getOccupancyForDesk = (deskId: number): OccupancyStatus | undefined => {
    return occupancyStatuses.value.find((status) => status.desk_id === deskId)
  }

  const isDeskOccupied = (deskId: number): boolean => {
    const status = getOccupancyForDesk(deskId)
    return status?.occupied ?? false
  }

  const getOccupiedDesks = () => {
    return occupancyStatuses.value.filter((status) => status.occupied)
  }

  const getAvailableDesks = () => {
    return occupancyStatuses.value.filter((status) => !status.occupied)
  }

  // Start auto-refresh
  const startAutoRefresh = () => {
    if (intervalId.value) return // Already running

    intervalId.value = window.setInterval(() => {
      fetchAllOccupancy()
    }, refreshInterval)
  }

  // Stop auto-refresh
  const stopAutoRefresh = () => {
    if (intervalId.value) {
      clearInterval(intervalId.value)
      intervalId.value = null
    }
  }

  // Initial load and auto-refresh setup
  onMounted(() => {
    fetchAllOccupancy()

    if (autoRefresh) {
      startAutoRefresh()
    }
  })

  // Cleanup
  onUnmounted(() => {
    stopAutoRefresh()
  })

  return {
    occupancyStatuses,
    isLoading,
    error,
    fetchAllOccupancy,
    getOccupancyForDesk,
    isDeskOccupied,
    getOccupiedDesks,
    getAvailableDesks,
    startAutoRefresh,
    stopAutoRefresh,
  }
}
