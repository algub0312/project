<!-- src/components/admin/AdminDeskStatusDialog.vue -->
<script setup lang="ts">
import type { Desk } from '@/types/desk.ts'
import type { DeskStatus } from '@/types/deskStatus.ts'

defineProps<{
  modelValue: boolean
  desk: Desk | null
  status: DeskStatus
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'update:status': [value: DeskStatus]
  confirm: []
}>()

const statusItems = [
  { title: 'Available', value: 'available' },
  { title: 'Occupied', value: 'occupied' },
  { title: 'Reserved', value: 'reserved' },
  { title: 'Maintenance', value: 'maintenance' },
]
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    max-width="500"
  >
    <v-card>
      <v-card-title class="text-h5"> Update Desk Status </v-card-title>

      <v-card-text>
        <div class="mb-4">
          <v-alert type="info" variant="tonal" density="compact" class="mb-4">
            <div class="text-center">
              <div class="text-caption">Selected Desk</div>
              <div class="text-h5 font-weight-bold">{{ desk?.id }}</div>
            </div>
          </v-alert>

          <v-select
            :model-value="status"
            @update:model-value="emit('update:status', $event)"
            :items="statusItems"
            label="New Status"
            variant="outlined"
            density="comfortable"
          />

          <v-alert v-if="desk" type="warning" variant="tonal" density="compact" class="mt-4">
            Current status: <strong>{{ desk.status }}</strong>
            <span v-if="desk.bookedBy">
              | Booked by: <strong>{{ desk.bookedBy }}</strong>
            </span>
          </v-alert>
        </div>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey" variant="text" @click="emit('update:modelValue', false)">
          Cancel
        </v-btn>
        <v-btn color="primary" variant="flat" @click="emit('confirm')"> Update Status </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
