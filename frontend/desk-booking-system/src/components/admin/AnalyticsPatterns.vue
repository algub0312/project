<script setup lang="ts">
import TimeTrackChart from './Charts/TimeTrackChart.vue'
import DeskOccupancyChart from './Charts/DeskOccupancyChart.vue'
import FloorChart from './Charts/FloorChart.vue'
import ActiveBookingsTable from './Charts/ActiveBookingsTable.vue'
</script>

<template>
  <v-container>
    <v-row>
      <v-col cols="2" sm="8">
        <v-row>
          <v-col cols="2" sm="6">
            <DeskOccupancyChart></DeskOccupancyChart>
          </v-col>
          <v-col cols="2" sm="6">
            <FloorChart></FloorChart>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="1" sm="12">
            <TimeTrackChart></TimeTrackChart>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="2" sm="4">
        <v-card>
          <v-card-text class="text-center pa-3">
            <div class="text-overline text-medium-emphasis" style="font-size: 0.65rem">
              Active Bookings
            </div>
            <ActiveBookingsTable></ActiveBookingsTable>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
