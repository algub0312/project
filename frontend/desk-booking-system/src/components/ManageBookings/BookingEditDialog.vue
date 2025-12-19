<script setup lang="ts">
import { ref, watch } from 'vue'
import type { BookingDisplay } from '@/utils/bookingAdminHelpers'

const props = defineProps<{
  modelValue: boolean
  booking: BookingDisplay | null
}>()

const emit = defineEmits(['update:modelValue', 'save'])

const localBooking = ref<BookingDisplay | null>(null)

const statusOptions = ['active', 'completed', 'cancelled']

watch(
  () => props.booking,
  (newBooking) => {
    if (newBooking) {
      localBooking.value = { ...newBooking }
    }
  },
  { immediate: true },
)

const handleSave = () => {
  if (localBooking.value) {
    emit('save', localBooking.value)
  }
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="500"
  >
    <v-card>
      <v-card-title class="text-h5">Edit Booking</v-card-title>
      <v-divider />
      <v-card-text v-if="localBooking" class="pt-4">
        <v-text-field
          v-model="localBooking.date"
          label="Date"
          type="date"
          variant="outlined"
          class="mb-3"
        />

        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model="localBooking.startTime"
              label="Start Time"
              type="time"
              variant="outlined"
            />
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model="localBooking.endTime"
              label="End Time"
              type="time"
              variant="outlined"
            />
          </v-col>
        </v-row>

        <v-select
          v-model="localBooking.status"
          :items="statusOptions"
          label="Status"
          variant="outlined"
          class="mb-3"
        />

        <v-textarea v-model="localBooking.notes" label="Notes" variant="outlined" rows="3" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:modelValue', false)"> Cancel </v-btn>
        <v-btn color="primary" variant="flat" @click="handleSave"> Save Changes </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
