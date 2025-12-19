<!-- src/components/admin/AdminFiltersBar.vue -->
<script setup lang="ts">
import type { DeskStatus } from '@/types/deskStatus.ts'

defineProps<{
  statusFilter: DeskStatus | 'all'
  selectedFloor: number
}>()

const emit = defineEmits<{
  'update:statusFilter': [value: DeskStatus | 'all']
  'update:selectedFloor': [value: number]
}>()

const statusItems = [
  { title: 'All Desks', value: 'all' },
  { title: 'Available Only', value: 'available' },
  { title: 'Occupied Only', value: 'occupied' },
  { title: 'Reserved Only', value: 'reserved' },
  { title: 'Maintenance Only', value: 'maintenance' },
]
</script>

<template>
  <v-row class="mb-4">
    <v-col cols="12">
      <div class="d-flex flex-wrap justify-space-between align-center ga-4">
        <!-- Status Filter -->
        <v-select
          :model-value="statusFilter"
          @update:model-value="emit('update:statusFilter', $event)"
          :items="statusItems"
          label="Filter by Status"
          variant="outlined"
          density="compact"
          hide-details
          style="max-width: 250px"
        />

        <!-- Floor Selector -->
        <v-btn-toggle
          :model-value="selectedFloor"
          @update:model-value="emit('update:selectedFloor', $event)"
          color="primary"
          mandatory
          rounded="lg"
        >
          <v-btn :value="0">
            <v-icon start>mdi-layers</v-icon>
            Floor 0
          </v-btn>
          <v-btn :value="1">
            <v-icon start>mdi-layers</v-icon>
            Floor 1
          </v-btn>
        </v-btn-toggle>
      </div>
    </v-col>
  </v-row>
</template>
