<script setup lang="ts">
import AnalyticsPatterns from '@/components/admin/AnalyticsPatterns.vue'
import RequireRole from '@/components/RequireRole.vue'
</script>

<template>
  <RequireRole :roles="['admin']">
    <v-container fluid class="analytics-view pa-6">
      <v-row class="mb-6">
        <v-col cols="12">
          <div class="pa-4">
            <h1 class="text-h4 font-weight-bold">Analytics</h1>
            <p class="text-body-1 text-medium-emphasis mt-2">
              See the users' patterns, statistics, and tendencies
            </p>
          </div>
        </v-col>
      </v-row>
      <analytics-patterns></analytics-patterns>
    </v-container>
  </RequireRole>
</template>

<style scoped>
.analytics-view {
  min-height: 100vh;
}
</style>
