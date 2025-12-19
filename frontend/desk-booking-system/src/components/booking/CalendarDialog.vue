<script setup lang="ts">
import type { Booking } from '@/types/mockData'
import { hoursBetween } from '@/utils/datetime'

const props = defineProps<{
  modelValue: boolean
  weekDays: { dayName: string; date: string; isToday: boolean }[]
  bookings: Booking[]
}>()
const emits = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()
</script>

<template>
  <v-dialog
    :model-value="props.modelValue"
    @update:model-value="emits('update:modelValue', $event)"
    max-width="800px"
  >
    <v-card>
      <v-card-title class="text-h5 pa-4">My Bookings Calendar</v-card-title>
      <v-card-text class="pa-4">
        <v-row class="mb-4">
          <v-col cols="12">
            <h3 class="text-h6 mb-2">This Week</h3>
            <div class="week-grid">
              <div
                v-for="d in props.weekDays"
                :key="d.date"
                class="day-column"
                :class="{ today: d.isToday }"
              >
                <div class="day-header">
                  <div class="font-weight-bold">{{ d.dayName }}</div>
                  <div class="text-caption">{{ new Date(d.date).getDate() }}</div>
                </div>
                <div class="bookings-list">
                  <v-card
                    v-for="b in props.bookings.filter((b) => b.date === d.date)"
                    :key="b.id"
                    class="booking-card mb-2"
                    elevation="1"
                  >
                    <v-card-text class="pa-2">
                      <div class="text-body-2 font-weight-bold">{{ b.deskId }}</div>
                      <div class="text-caption">{{ b.startTime }} - {{ b.endTime }}</div>
                      <div class="text-caption text-grey">
                        {{ hoursBetween(b.startTime, b.endTime) }}h
                      </div>
                    </v-card-text>
                  </v-card>
                  <div
                    v-if="props.bookings.filter((b) => b.date === d.date).length === 0"
                    class="text-caption text-grey pa-2"
                  >
                    No bookings
                  </div>
                </div>
              </div>
            </div>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <h3 class="text-h6 mb-2">All My Bookings</h3>
            <v-list>
              <v-list-item v-for="b in props.bookings.slice().reverse()" :key="b.id" class="mb-2">
                <template #prepend
                  ><v-avatar color="primary"><v-icon>mdi-desk</v-icon></v-avatar></template
                >
                <v-list-item-title>{{ b.deskId }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{
                    new Date(b.date).toLocaleDateString('en-GB', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                    })
                  }}
                  • {{ b.startTime }} - {{ b.endTime }} •
                  {{ hoursBetween(b.startTime, b.endTime) }} hours
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="primary" variant="flat" @click="emits('update:modelValue', false)"
          >Close</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}
.day-column {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  min-height: 150px;
}
.day-column.today {
  border: 2px solid #2196f3;
  background-color: rgba(33, 150, 243, 0.05);
}
.day-header {
  background-color: #f5f5f5;
  padding: 8px;
  text-align: center;
  border-bottom: 1px solid #e0e0e0;
}
.day-column.today .day-header {
  background-color: #2196f3;
  color: #fff;
}
.bookings-list {
  padding: 8px;
}
.booking-card {
  background-color: #e3f2fd !important;
  border-left: 3px solid #2196f3;
}
@media (max-width: 960px) {
  .week-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 600px) {
  .week-grid {
    grid-template-columns: 1fr;
  }
}
</style>
