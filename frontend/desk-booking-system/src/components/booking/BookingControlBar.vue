<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  start: Date
  end: Date
}>()

const emit = defineEmits<{
  (e: 'update:start', value: Date): void
  (e: 'update:end', value: Date): void
}>()

// hours from 6 AM to 18 PM
const hours = Array.from({ length: 13 }, (_, i) => i + 6)

const dateMenu = ref(false)
const datePickerValue = ref<Date>(props.start)
const selectedHour = ref(props.start.getHours())

const formattedDate = computed(() => {
  return props.start.toLocaleDateString(undefined, {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
})

const formattedTime = computed(() => {
  const startTime = props.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  const endTime = props.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return `${startTime} – ${endTime}`
})

function updateDateTime(date: Date, hour: number) {
  const newStart = new Date(date)
  newStart.setHours(hour, 0, 0, 0)
  const newEnd = new Date(newStart)
  newEnd.setHours(newStart.getHours() + 1)

  emit('update:start', newStart)
  emit('update:end', newEnd)
}

function changeDay(offset: number) {
  const d = new Date(props.start)
  d.setDate(d.getDate() + offset)
  datePickerValue.value = d
  updateDateTime(d, selectedHour.value)
}

function setToday() {
  const d = new Date()
  const h = d.getHours()
  selectedHour.value = h
  datePickerValue.value = d
  updateDateTime(d, h)
}

watch(datePickerValue, (newDate) => {
  if (newDate) {
    updateDateTime(newDate, selectedHour.value)
  }
})

watch(selectedHour, (h) => {
  updateDateTime(props.start, h)
})
</script>

<template>
  <div class="booking-control-bar px-4 py-3 d-flex flex-column gap-3">
    <div class="d-flex align-center justify-space-between flex-wrap gap-2">
      <div class="d-flex align-center gap-2">
        <v-btn variant="outlined" rounded="xl" @click="setToday">Today</v-btn>
      </div>
      <v-menu v-model="dateMenu">
        <template #activator="{ props }">
          <div>
            <v-btn class="ma-2" icon="mdi-chevron-left" size="small" @click="changeDay(-1)" />
            <v-btn v-bind="props" prepend-icon="mdi-calendar">
              {{ formattedDate }}
            </v-btn>
            <v-btn class="ma-2" icon="mdi-chevron-right" size="small" @click="changeDay(1)" />
          </div>
        </template>
        <v-date-picker
          v-model="datePickerValue"
          hide-actions
          @update:model-value="dateMenu = false"
        />
      </v-menu>
      <div class="text-body-2 text-medium-emphasis">
        {{ formattedTime }}
      </div>
    </div>
    <div>
      <v-slider
        v-model="selectedHour"
        :min="hours[0]"
        :max="hours[hours.length - 1]"
        step="1"
        show-ticks="always"
        tick-size="2"
        prepend-icon="mdi-clock-outline"
      />
    </div>
  </div>
</template>

<style scoped>
.booking-control-bar {
  border-bottom: 1px solid #eee;
}
</style>
