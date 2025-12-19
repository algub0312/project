<script setup lang="ts">
import { mockDataHelpers } from '@/types/mockData'
import { ref } from 'vue'

const activeBookings = ref(mockDataHelpers.bookings.getActive())

const headers = [
  { title: 'Desk', key: 'deskId' },
  { title: 'Started At', key: 'startedAt' },
  { title: 'Ends At', key: 'endsAt' },
]
</script>

<template>
  <v-row class="mt-4">
    <v-col cols="12">
      <v-card elevation="2">
        <v-card-text class="pa-0">
          <v-data-table
            :headers="headers"
            :items="activeBookings"
            item-key="id"
            :items-per-page="8"
            class="elevation-0"
            hover
          >
            <template #item="{ item }">
              <tr>
                <td>{{ item.deskId }}</td>
                <td>{{ item.startTime }}</td>
                <td>{{ item.endTime }}</td>
              </tr>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
