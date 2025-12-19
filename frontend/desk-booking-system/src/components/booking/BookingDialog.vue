<script setup lang="ts">
import { ref, watch, computed } from 'vue'

const props = defineProps<{
  modelValue: boolean
  deskId?: number
  start: Date
  end: Date
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'update:start', v: Date): void
  (e: 'update:end', v: Date): void
  (e: 'confirm'): void
}>()

// Local editable state, initialized from props
const localDate = ref('')
const localStartTime = ref('')
const localEndTime = ref('')

// Initialize local state when dialog opens or props change
watch(
  [() => props.modelValue, () => props.start, () => props.end],
  () => {
    if (props.modelValue) {
      // Format date as YYYY-MM-DD for date input
      const year = props.start.getFullYear()
      const month = String(props.start.getMonth() + 1).padStart(2, '0')
      const day = String(props.start.getDate()).padStart(2, '0')
      localDate.value = `${year}-${month}-${day}`

      // Format times as HH:MM for time inputs
      const startHours = String(props.start.getHours()).padStart(2, '0')
      const startMinutes = String(props.start.getMinutes()).padStart(2, '0')
      localStartTime.value = `${startHours}:${startMinutes}`

      const endHours = String(props.end.getHours()).padStart(2, '0')
      const endMinutes = String(props.end.getMinutes()).padStart(2, '0')
      localEndTime.value = `${endHours}:${endMinutes}`
    }
  },
  { immediate: true },
)

// Update parent when local values change
watch([localDate, localStartTime, localEndTime], () => {
  if (localDate.value && localStartTime.value && localEndTime.value) {
    const newStart = new Date(`${localDate.value}T${localStartTime.value}:00`)
    const newEnd = new Date(`${localDate.value}T${localEndTime.value}:00`)

    if (!isNaN(newStart.getTime()) && !isNaN(newEnd.getTime())) {
      emits('update:start', newStart)
      emits('update:end', newEnd)
    }
  }
})

const todayISO = computed(() => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})
</script>

<template>
  <v-dialog
    :model-value="props.modelValue"
    @update:model-value="emits('update:modelValue', $event)"
    max-width="500px"
  >
    <v-card>
      <v-card-title class="text-h5 pa-4">Book Desk {{ props.deskId }}</v-card-title>
      <v-card-text class="pa-4">
        <v-text-field
          v-model="localDate"
          label="Date"
          type="date"
          :min="todayISO"
          variant="outlined"
          class="mb-4"
          prepend-inner-icon="mdi-calendar"
        />
        <v-text-field
          v-model="localStartTime"
          label="Start Time"
          type="time"
          variant="outlined"
          class="mb-4"
          prepend-inner-icon="mdi-clock-start"
        />
        <v-text-field
          v-model="localEndTime"
          label="End Time"
          type="time"
          variant="outlined"
          class="mb-4"
          prepend-inner-icon="mdi-clock-end"
        />
        <v-alert type="info" variant="tonal" class="mb-0">
          <div class="text-body-2">
            <strong>Booking Summary:</strong><br />
            Desk: {{ props.deskId }}<br />
            Date: {{ localDate }}<br />
            Time: {{ localStartTime }} - {{ localEndTime }}
          </div>
        </v-alert>
      </v-card-text>
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="grey" variant="text" @click="emits('update:modelValue', false)">
          Cancel
        </v-btn>
        <v-btn color="primary" variant="flat" @click="emits('confirm')"> Confirm Booking </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
