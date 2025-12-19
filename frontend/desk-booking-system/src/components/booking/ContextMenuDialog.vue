<script setup lang="ts">
import type { Desk } from '@/types/desk.ts'
const props = defineProps<{
  modelValue: boolean
  desk: Desk | null
}>()
const emits = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'quick', hours: number): void
  (e: 'half'): void
  (e: 'full'): void
  (e: 'favorite'): void
  (e: 'weekly'): void
}>()
</script>

<template>
  <v-dialog
    :model-value="props.modelValue"
    @update:model-value="emits('update:modelValue', $event)"
    max-width="400px"
  >
    <v-card>
      <v-card-title class="text-h6 pa-4">Quick Actions - Desk {{ props.desk?.id }}</v-card-title>
      <v-list>
        <v-list-item @click="emits('quick', 2)">
          <template #prepend><v-icon color="primary">mdi-clock-fast</v-icon></template>
          <v-list-item-title>Book for 2 hours</v-list-item-title>
          <v-list-item-subtitle>From now until 2 hours later</v-list-item-subtitle>
        </v-list-item>
        <v-list-item @click="emits('half')">
          <template #prepend><v-icon color="primary">mdi-clock-time-four</v-icon></template>
          <v-list-item-title>Book for half day</v-list-item-title>
          <v-list-item-subtitle>09:00 - 13:00</v-list-item-subtitle>
        </v-list-item>
        <v-list-item @click="emits('full')">
          <template #prepend><v-icon color="primary">mdi-clock-outline</v-icon></template>
          <v-list-item-title>Book for full day</v-list-item-title>
          <v-list-item-subtitle>09:00 - 17:00</v-list-item-subtitle>
        </v-list-item>
        <v-divider class="my-2" />
        <v-list-item @click="emits('favorite')">
          <template #prepend><v-icon>mdi-heart</v-icon></template>
          <v-list-item-title>Toggle favorite</v-list-item-title>
        </v-list-item>
        <v-list-item @click="emits('weekly')">
          <template #prepend><v-icon color="primary">mdi-calendar-week</v-icon></template>
          <v-list-item-title>View weekly availability</v-list-item-title>
        </v-list-item>
      </v-list>
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="grey" variant="text" @click="emits('update:modelValue', false)">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
