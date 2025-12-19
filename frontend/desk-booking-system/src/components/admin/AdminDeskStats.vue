<script setup lang="ts">
interface Stats {
  total: number
  available: number
  occupied: number
  reserved: number
  maintenance: number
}

defineProps<{
  stats: Stats
}>()
</script>

<template>
  <v-row class="mb-6">
    <v-col cols="6" sm="4" md="2">
      <v-card>
        <v-card-text class="text-center pa-3">
          <div class="text-overline text-medium-emphasis" style="font-size: 0.65rem">Total</div>
          <div class="text-h5 font-weight-bold">{{ stats.total }}</div>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="6" sm="4" md="2">
      <v-card color="success" variant="tonal">
        <v-card-text class="text-center pa-3">
          <div class="text-overline" style="font-size: 0.65rem">Available</div>
          <div class="text-h5 font-weight-bold">{{ stats.available }}</div>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="6" sm="4" md="2">
      <v-card color="error" variant="tonal">
        <v-card-text class="text-center pa-3">
          <div class="text-overline" style="font-size: 0.65rem">Occupied</div>
          <div class="text-h5 font-weight-bold">{{ stats.occupied }}</div>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="6" sm="4" md="2">
      <v-card color="warning" variant="tonal">
        <v-card-text class="text-center pa-3">
          <div class="text-overline" style="font-size: 0.65rem">Reserved</div>
          <div class="text-h5 font-weight-bold">{{ stats.reserved }}</div>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="6" sm="4" md="3">
      <v-card color="grey" variant="tonal">
        <v-card-text class="text-center pa-3">
          <div class="text-overline" style="font-size: 0.65rem">Maintenance</div>
          <div class="text-h5 font-weight-bold">{{ stats.maintenance }}</div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
