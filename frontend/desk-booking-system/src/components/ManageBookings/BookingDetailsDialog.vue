<script setup lang="ts">
import BookingDetailItem from './BookingDetailItem.vue'
import {
  formatDate,
  formatDateTime,
  getStatusColor,
  normalizeStatus,
} from '@/utils/bookingAdminHelpers'
import type { BookingDisplay } from '@/utils/bookingAdminHelpers'

defineProps<{
  modelValue: boolean
  booking: BookingDisplay | null
}>()

defineEmits(['update:modelValue'])
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="600"
  >
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <span class="text-h5">Booking Details</span>
        <v-btn icon="mdi-close" variant="text" @click="$emit('update:modelValue', false)" />
      </v-card-title>
      <v-divider />
      <v-card-text v-if="booking" class="pt-4">
        <v-list>
          <BookingDetailItem
            icon="mdi-account"
            color="primary"
            title="User"
            :subtitle="`${booking.userName} (${booking.userEmail})`"
          />

          <BookingDetailItem
            icon="mdi-desk"
            color="info"
            title="Desk"
            :subtitle="`${booking.deskName} - Floor ${booking.floor}`"
          />

          <BookingDetailItem
            icon="mdi-calendar"
            color="success"
            title="Date"
            :subtitle="formatDate(booking.date)"
          />

          <BookingDetailItem
            icon="mdi-clock"
            color="warning"
            title="Time Slot"
            :subtitle="booking.timeSlot"
          />

          <v-list-item>
            <template v-slot:prepend>
              <v-icon :color="getStatusColor(booking.status)"> mdi-information </v-icon>
            </template>
            <v-list-item-title>Status</v-list-item-title>
            <v-list-item-subtitle>
              <v-chip :color="getStatusColor(booking.status)" size="small" variant="flat">
                {{ normalizeStatus(booking.status) }}
              </v-chip>
            </v-list-item-subtitle>
          </v-list-item>

          <BookingDetailItem
            icon="mdi-clock-outline"
            color="secondary"
            title="Created At"
            :subtitle="formatDateTime(booking.createdAt)"
          />

          <BookingDetailItem
            v-if="booking.notes"
            icon="mdi-note-text"
            color="grey"
            title="Notes"
            :subtitle="booking.notes"
          />
        </v-list>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
