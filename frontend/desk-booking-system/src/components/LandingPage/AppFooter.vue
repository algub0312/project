<script setup lang="ts"></script>

<template>
  <footer class="footer">
    <v-container>
      <v-row>
        <v-col cols="12" md="4">
          <div class="d-flex align-center mb-3">
            <v-avatar color="primary" size="32" class="mr-2">
              <v-icon size="18" color="white">mdi-desk</v-icon>
            </v-avatar>
            <span class="text-h6 font-weight-bold">DeskBooking</span>
          </div>
          <p class="text-grey-darken-1">
            Smart desk management for modern workplaces with IoT integration.
          </p>
        </v-col>

        <v-col cols="6" md="2">
          <h4 class="font-weight-bold mb-3">Product</h4>
          <div class="footer-links">
            <a href="#">Features</a><a href="#">How it works</a><a href="#">Technology</a>
          </div>
        </v-col>

        <v-col cols="6" md="2">
          <h4 class="font-weight-bold mb-3">Company</h4>
          <div class="footer-links">
            <a href="#">About</a><a href="#">Contact</a><a href="#">Documentation</a>
          </div>
        </v-col>

        <v-col cols="12" md="4">
          <h4 class="font-weight-bold mb-3">Stay updated</h4>
          <v-text-field
            placeholder="Enter your email"
            variant="outlined"
            density="compact"
            append-inner-icon="mdi-send"
            hide-details
          />
        </v-col>
      </v-row>

      <v-divider class="my-6" />
      <div class="text-center text-grey">
        <p>&copy; 2025 DeskBooking System - SDU Group 7</p>
      </div>
    </v-container>
  </footer>
</template>

<style scoped>
.footer {
  padding: 60px 0 20px;
}
.footer-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.footer a {
  text-decoration: none;
  transition: color 0.2s;
}
:root .footer {
  background: #f5f5f5;
}
.v-theme--dark .footer {
  background: #212121;
}
</style>
