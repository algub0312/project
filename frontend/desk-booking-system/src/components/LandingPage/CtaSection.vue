<script setup lang="ts">
import { useAuthStore } from '@/stores/auth.ts'
const authStore = useAuthStore()
</script>

<template>
  <section class="cta">
    <v-container class="text-center">
      <h2 class="section-title mb-4">Ready to transform your office?</h2>
      <p class="text-h6 text-grey-darken-1 mb-6">
        Join forward-thinking companies optimizing their workspace
      </p>
      <v-btn size="x-large" color="primary" rounded elevation="4" @click="authStore.login()">
        Get Started Now
        <v-icon end>mdi-arrow-right</v-icon>
      </v-btn>
    </v-container>
  </section>
</template>

<style scoped>
.cta {
  padding: 80px 0;
}
:root .cta {
  background: #fff;
}
.v-theme--dark .cta {
  background: #1a1a1a;
}
.section-title {
  font-size: 2.5rem;
  font-weight: 800;
}
</style>
