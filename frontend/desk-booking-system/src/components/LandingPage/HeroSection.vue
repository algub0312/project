<script setup lang="ts">
import { useAuthStore } from '@/stores/auth.ts'
const authStore = useAuthStore()
</script>

<template>
  <section class="hero">
    <v-container>
      <v-row align="center">
        <v-col cols="12" md="6">
          <v-chip color="primary" class="mb-4">
            <v-icon start>mdi-office-building</v-icon>
            Smart Office Management
          </v-chip>

          <h1 class="hero-title mb-4">
            Transform your workspace with <span class="text-primary">smart desk booking</span>
          </h1>

          <p class="hero-subtitle mb-6">
            Maximize office efficiency with our intelligent desk management system. Book, monitor,
            and optimize your workspace seamlessly.
          </p>

          <div class="d-flex flex-wrap ga-3 mb-8">
            <v-btn size="large" color="primary" rounded @click="authStore.login()">
              Start Booking
              <v-icon end>mdi-arrow-right</v-icon>
            </v-btn>
          </div>

          <div class="d-flex align-center ga-4">
            <v-avatar color="blue" size="40" />
            <v-avatar color="purple" size="40" />
            <v-avatar color="teal" size="40" />
            <div>
              <v-rating :model-value="5" color="amber" density="compact" readonly size="small" />
              <p class="text-caption text-grey">Trusted by modern offices</p>
            </div>
          </div>
        </v-col>

        <v-col cols="12" md="6">
          <v-card class="preview-card" elevation="8">
            <v-card-text class="pa-6">
              <div class="d-flex align-center mb-4">
                <v-avatar color="primary" size="40" class="mr-3">
                  <v-icon>mdi-calendar-check</v-icon>
                </v-avatar>
                <div>
                  <h3 class="text-h6 font-weight-bold">Available Desks</h3>
                  <p class="text-caption text-grey">Today</p>
                </div>
              </div>

              <v-card color="grey-lighten-4" class="pa-4 mb-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <div>
                    <h4 class="font-weight-bold">Desk #A-42</h4>
                    <p class="text-caption text-grey">Window seat • Adjustable</p>
                  </div>
                  <v-chip color="success" size="small">Available</v-chip>
                </div>

                <div class="d-flex flex-wrap ga-2 mb-3">
                  <v-chip size="small" variant="outlined">
                    <v-icon start size="small">mdi-monitor</v-icon>
                    Dual monitors
                  </v-chip>
                  <v-chip size="small" variant="outlined">
                    <v-icon start size="small">mdi-wifi</v-icon>
                    High-speed
                  </v-chip>
                </div>

                <v-btn color="primary" block @click="authStore.login()">Book Now</v-btn>
              </v-card>

              <div class="d-flex justify-space-between align-center">
                <span class="text-caption text-grey">15 desks available</span>
                <v-btn size="small" variant="text" color="primary" @click="authStore.login()">
                  View All
                  <v-icon end size="small">mdi-arrow-right</v-icon>
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </section>
</template>

<style scoped>
.hero {
  padding: 80px 0;
  min-height: 600px;
  display: flex;
  align-items: center;
}
.hero-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.2;
}
.hero-subtitle {
  font-size: 1.25rem;
  max-width: 90%;
}
.preview-card {
  border-radius: 16px;
  transition: transform 0.3s ease;
}
.preview-card:hover {
  transform: translateY(-8px);
}
:root .hero {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 50%, #e0f2f1 100%);
}
.v-theme--dark .hero {
  background: linear-gradient(135deg, #0d47a1 0%, #00695c 50%, #37474f 100%);
}
</style>
