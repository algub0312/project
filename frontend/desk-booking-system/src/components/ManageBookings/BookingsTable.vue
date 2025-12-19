<script setup lang="ts">
import BookingUserCell from './BookingUserCell.vue'
import BookingDeskCell from './BookingDeskCell.vue'
import BookingDateCell from './BookingDateCell.vue'
import BookingActions from './BookingActions.vue'
import { formatDateTime, getStatusColor, normalizeStatus } from '@/utils/bookingAdminHelpers'
import type { BookingDisplay } from '@/utils/bookingAdminHelpers'

defineProps<{
  bookings: BookingDisplay[]
  loading?: boolean
}>()

defineEmits(['view', 'edit', 'cancel', 'delete'])

const headers = [
  { title: 'User', key: 'user', sortable: true },
  { title: 'Desk', key: 'desk', sortable: true },
  { title: 'Date & Time', key: 'date', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Created', key: 'createdAt', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' as const },
]
</script>

<template>
  <v-row class="mt-4">
    <v-col cols="12">
      <v-card elevation="2">
        <v-card-text class="pa-0">
          <v-data-table
            :headers="headers"
            :items="bookings"
            :loading="loading"
            :items-per-page="10"
            class="elevation-0"
          >
            <template v-slot:item.user="{ item }">
              <BookingUserCell :booking="item" />
            </template>

            <template v-slot:item.desk="{ item }">
              <BookingDeskCell :booking="item" />
            </template>

            <template v-slot:item.date="{ item }">
              <BookingDateCell :booking="item" />
            </template>

            <template v-slot:item.status="{ item }">
              <v-chip :color="getStatusColor(item.status)" size="small" variant="flat">
                {{ normalizeStatus(item.status) }}
              </v-chip>
            </template>

            <template v-slot:item.createdAt="{ item }">
              <div class="text-caption">
                {{ formatDateTime(item.createdAt) }}
              </div>
            </template>

            <template v-slot:item.actions="{ item }">
              <BookingActions
                :booking="item"
                @view="$emit('view', item)"
                @edit="$emit('edit', item)"
                @cancel="$emit('cancel', item)"
                @delete="$emit('delete', item)"
              />
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<style scoped>
.v-data-table {
  background: transparent;
}
</style>
