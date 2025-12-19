<script setup lang="ts">
import { formatDate } from '@/utils/bookingAdminHelpers'
import type { BookingDisplay } from '@/utils/bookingAdminHelpers'

defineProps<{
  booking: BookingDisplay
}>()
</script>

<template>
  <div>
    <div class="font-weight-medium">
      {{ formatDate(booking.date) }}
    </div>
    <div class="text-caption text-medium-emphasis">
      {{ booking.timeSlot }}
    </div>
  </div>
</template>
