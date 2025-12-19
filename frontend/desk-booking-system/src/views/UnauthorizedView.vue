<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <v-app>
    <v-main>
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col class="text-center">
            <v-icon size="64" color="error">mdi-alert-circle-outline</v-icon>
            <h1>Unauthorized Access</h1>
            <p>You do not have permission to view this page.</p>
            <v-btn color="primary" class="mt-4" @click="router.push('/')">Go to Home</v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped></style>
