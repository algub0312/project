<script setup lang="ts">
import type { Desk } from '@/types/desk.ts'
const props = defineProps<{
  modelValue: boolean
  desk: Desk | undefined
  weekDays: { dayName: string; date: string; isToday: boolean }[]
  isBooked: (deskId: number, date: string) => { startTime: string; endTime: string } | undefined
}>()
const emits = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'book'): void
}>()
</script>

<template>
  <v-dialog
    :model-value="props.modelValue"
    @update:model-value="emits('update:modelValue', $event)"
    max-width="600px"
  >
    <v-card>
      <v-card-title class="text-h5 pa-4">Weekly Availability - Desk {{ desk?.id }}</v-card-title>
      <v-card-text class="pa-4">
        <v-row v-for="d in weekDays" :key="d.date" class="mb-3">
          <v-col cols="3" class="d-flex align-center">
            <div>
              <div class="font-weight-bold">{{ d.dayName }}</div>
              <div class="text-caption text-grey">{{ new Date(d.date).getDate() }}</div>
            </div>
          </v-col>
          <v-col cols="9">
            <template v-if="isBooked(props.desk!.id, d.date)">
              <v-chip color="error" size="small">
                <v-icon start size="small">mdi-close-circle</v-icon>
                Booked: {{ isBooked(props.desk!.id, d.date)?.startTime }} -
                {{ isBooked(props.desk!.id, d.date)?.endTime }}
              </v-chip>
            </template>
            <template v-else>
              <v-chip color="success" size="small">
                <v-icon start size="small">mdi-check-circle</v-icon>
                Available all day
              </v-chip>
            </template>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="grey" variant="text" @click="emits('update:modelValue', false)">Close</v-btn>
        <v-btn
          v-if="desk?.status === 'available'"
          color="primary"
          variant="flat"
          @click="emits('book')"
          >Book This Desk</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
