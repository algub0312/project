<script setup lang="ts">
import type { Stat } from '@/composables/useLandingData'
defineProps<{ stats: Stat[] }>()
</script>

<template>
  <section class="stats">
    <v-container>
      <v-row class="text-center">
        <v-col v-for="s in stats" :key="s.label" cols="12" md="4">
          <h2 class="stat-value mb-2">{{ s.value }}</h2>
          <p class="stat-label">{{ s.label }}</p>
        </v-col>
      </v-row>
    </v-container>
  </section>
</template>

<style scoped>
.stats {
  padding: 80px 0;
}
:root .stats {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 50%, #e0f2f1 100%);
}
.v-theme--dark .stats {
  background: linear-gradient(135deg, #1565c0 0%, #00796b 100%);
}
.stat-value {
  font-size: 3rem;
  font-weight: 800;
}
.stat-label {
  font-size: 1.25rem;
}
</style>
