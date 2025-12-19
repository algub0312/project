<script setup lang="ts">
import type { BookingDisplay } from '@/utils/bookingAdminHelpers'

defineProps<{
  booking: BookingDisplay
}>()
</script>

<template>
  <div>
    <v-chip size="small" color="info" variant="flat">
      {{ booking.deskName }}
    </v-chip>
    <div class="text-caption text-medium-emphasis mt-1">Floor: {{ booking.floor }}</div>
  </div>
</template>
