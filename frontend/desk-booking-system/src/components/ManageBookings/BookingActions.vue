<script setup lang="ts">
import type { BookingDisplay } from '@/utils/bookingAdminHelpers'

defineProps<{
  booking: BookingDisplay
}>()

defineEmits(['view', 'edit', 'cancel', 'delete'])
</script>

<template>
  <div class="d-flex gap-1">
    <v-tooltip text="View Details" location="top">
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          icon="mdi-eye"
          size="small"
          variant="text"
          color="info"
          @click="$emit('view')"
        />
      </template>
    </v-tooltip>

    <v-tooltip text="Edit Booking" location="top">
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          icon="mdi-pencil"
          size="small"
          variant="text"
          color="primary"
          @click="$emit('edit')"
        />
      </template>
    </v-tooltip>

    <v-tooltip text="Cancel Booking" location="top">
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          icon="mdi-close-circle"
          size="small"
          variant="text"
          color="warning"
          :disabled="booking.status === 'cancelled'"
          @click="$emit('cancel')"
        />
      </template>
    </v-tooltip>

    <v-tooltip text="Delete Booking" location="top">
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          icon="mdi-delete"
          size="small"
          variant="text"
          color="error"
          @click="$emit('delete')"
        />
      </template>
    </v-tooltip>
  </div>
</template>
