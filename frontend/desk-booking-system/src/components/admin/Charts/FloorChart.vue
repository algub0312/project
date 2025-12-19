<script setup lang="ts">
import { ref } from 'vue'
import { VPie } from 'vuetify/labs/VPie'
import { plByFloor } from '@/types/mockData'
const items = ref(plByFloor)
</script>

<template>
  <v-card>
    <v-card-text class="text-center pa-3">
      <div class="text-overline text-medium-emphasis" style="font-size: 0.65rem">
        Floor Distribution
      </div>
      <v-pie
        class="d-flex align-center justify-center"
        :gap="2"
        :gauge-cut="146"
        hide-slice
        :inner-cut="71"
        animation
        :palette="['#fa7e19', '#196ffa']"
        tooltip
        reveal
        :items="items"
      />
    </v-card-text>
  </v-card>
</template>
