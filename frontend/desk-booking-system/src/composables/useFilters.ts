import { ref, computed } from 'vue'

import type { Desk } from '@/types/desk.ts'

export function useFilters(desks: Readonly<{ value: Desk[] }>) {
  const searchQuery = ref('')
  const selectedStatus = ref<string[]>([])
  const selectedFeatures = ref<string[]>([])
  const quickFilter = ref<string | null>(null)

  const availableFeatures = [
    { value: 'near-window', label: 'Near Window', icon: 'mdi-window-closed-variant' },
    { value: 'dual-monitor', label: 'Dual Monitor', icon: 'mdi-monitor-multiple' },
  ]

  const filteredDesks = computed(() => {
    let result = desks.value
    const q = searchQuery.value.trim().toLowerCase()
    if (q) result = result.filter((d) => d.id.toString().includes(q))

    if (selectedStatus.value.length) {
      result = result.filter((d) => selectedStatus.value.includes(d.status))
    }

    if (selectedFeatures.value.length) {
      result = result.filter((d) => selectedFeatures.value.every((f) => d.features.includes(f)))
    }

    switch (quickFilter.value) {
      case 'available-now':
        result = result.filter((d) => d.status === 'available')
        break
      case 'available-today':
        result = result.filter((d) => ['available', 'reserved'].includes(d.status))
        break
      case 'my-bookings':
        result = result.filter((d) => d.bookedBy === 'current-user')
        break
      case 'favorites':
        result = result.filter((d) => !!d.isFavorite)
        break
    }
    return result
  })

  const toggleQuickFilter = (f: string) => {
    quickFilter.value = quickFilter.value === f ? null : f
  }
  const clearFilters = () => {
    searchQuery.value = ''
    selectedStatus.value = []
    selectedFeatures.value = []
    quickFilter.value = null
  }
  const hasActiveFilters = computed(
    () =>
      !!searchQuery.value ||
      selectedStatus.value.length > 0 ||
      selectedFeatures.value.length > 0 ||
      quickFilter.value !== null,
  )

  return {
    searchQuery,
    selectedStatus,
    selectedFeatures,
    availableFeatures,
    filteredDesks,
    toggleQuickFilter,
    clearFilters,
    hasActiveFilters,
  }
}
