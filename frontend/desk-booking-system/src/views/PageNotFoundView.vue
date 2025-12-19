<script setup lang="ts"></script>

<template>
  <v-app>
    <v-main>
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col class="text-center">
            <v-icon size="64" color="error">mdi-alert-circle-outline</v-icon>
            <h1>404 - Page Not Found</h1>
            <p>The page you are looking for does not exist.</p>
            <v-btn color="primary" class="mt-4" to="/">Go to Home</v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped></style>
