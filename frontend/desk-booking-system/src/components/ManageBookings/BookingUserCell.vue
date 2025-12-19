<script setup lang="ts">
import { getUserInitials } from '@/utils/bookingAdminHelpers'
import type { BookingDisplay } from '@/utils/bookingAdminHelpers'

defineProps<{
  booking: BookingDisplay
}>()
</script>

<template>
  <div class="d-flex align-center py-2">
    <v-avatar color="primary" size="32" class="mr-3">
      <span class="text-white text-body-2">
        {{ getUserInitials(booking.userName) }}
      </span>
    </v-avatar>
    <div>
      <div class="font-weight-medium">{{ booking.userName }}</div>
      <div class="text-caption text-medium-emphasis">
        {{ booking.userEmail }}
      </div>
    </div>
  </div>
</template>
