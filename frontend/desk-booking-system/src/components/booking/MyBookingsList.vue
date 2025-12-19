<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Booking } from '@/types/mockData'
import deskPhoto from '@/assets/deskPhoto.png'
import { deskIntegrationService } from '@/services/api/deskIntegrationService.ts'
import type { Desk } from '@/types/desk.ts'

const props = defineProps<{
  desks: Desk[]
  bookings: Booking[]
  currentUser: string
}>()

// Reactive state for desk controls
const currentHeight = ref<number>(680)
const standingHeight = ref<number>(1120)
const sittingHeight = ref<number>(700)
const customPosition = ref<number | null>(null)
const loading = ref(false)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success' as 'success' | 'error' | 'warning' | 'info',
})

// Get the current user's booked desk
const getCurrentBookedDesk = () => {
  return props.desks.find((d) => d.bookedBy === props.currentUser)
}

// Fetch current desk state
const fetchDeskState = async () => {
  const desk = getCurrentBookedDesk()
  if (!desk) return

  try {
    const state = await deskIntegrationService.getDeskState(desk.id)
    if (state && state.position_mm) {
      currentHeight.value = state.position_mm
    }
  } catch (error) {
    console.error('Failed to fetch desk state:', error)
  }
}

// Set desk to standing height
const setStandingHeight = async () => {
  const desk = getCurrentBookedDesk()
  if (!desk) return

  loading.value = true
  try {
    const state = await deskIntegrationService.setDeskHeight(desk.id, standingHeight.value)
    if (state && state.position_mm) {
      currentHeight.value = state.position_mm
      showSnackbar('Desk set to standing height', 'success')
    }
  } catch (error) {
    console.error('Failed to set standing height:', error)
    showSnackbar('Failed to set standing height', 'error')
  } finally {
    loading.value = false
  }
}

// Set desk to sitting height
const setSittingHeight = async () => {
  const desk = getCurrentBookedDesk()
  if (!desk) return

  loading.value = true
  try {
    const state = await deskIntegrationService.setDeskHeight(desk.id, sittingHeight.value)
    if (state && state.position_mm) {
      currentHeight.value = state.position_mm
      showSnackbar('Desk set to sitting height', 'success')
    }
  } catch (error) {
    console.error('Failed to set sitting height:', error)
    showSnackbar('Failed to set sitting height', 'error')
  } finally {
    loading.value = false
  }
}

// Set desk to custom position
const setCustomPosition = async () => {
  const desk = getCurrentBookedDesk()
  if (!desk || !customPosition.value) return

  loading.value = true
  try {
    const state = await deskIntegrationService.setDeskHeight(desk.id, customPosition.value)
    if (state && state.position_mm) {
      currentHeight.value = state.position_mm
      showSnackbar(`Desk set to ${customPosition.value}mm`, 'success')
      customPosition.value = null
    }
  } catch (error) {
    console.error('Failed to set custom position:', error)
    showSnackbar('Failed to set custom position', 'error')
  } finally {
    loading.value = false
  }
}

// Show snackbar notification
const showSnackbar = (text: string, color: 'success' | 'error' | 'warning' | 'info') => {
  snackbar.value = { show: true, text, color }
}

// Fetch desk state on mount
onMounted(() => {
  fetchDeskState()
})
</script>

<template>
  <v-card elevation="2" class="pa-6 mt-4">
    <v-row class="mb-4">
      <v-col>
        <h2 class="text-h5 font-weight-bold">My Current Booking</h2>
      </v-col>
    </v-row>

    <v-row class="justify-center">
      <v-col cols="12" md="10" lg="8" xl="6">
        <v-alert
          v-if="props.desks.filter((d) => d.bookedBy === props.currentUser).length === 0"
          type="info"
          variant="tonal"
          class="mb-4"
        >
          No active bookings. Click on an available desk to make a reservation.
        </v-alert>

        <div v-else>
          <v-card
            v-for="desk in props.desks.filter((d) => d.bookedBy === props.currentUser)"
            :key="desk.id"
            elevation="3"
            class="booking-detail-card mb-4"
          >
            <v-row no-gutters>
              <!-- IMAGE -->
              <v-col cols="12" md="4">
                <div class="image-wrapper">
                  <v-img
                    :src="deskPhoto"
                    alt="Desk"
                    height="300"
                    contain
                    position="center center"
                    class="rounded-lg"
                  >
                    <template #placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-icon size="64" color="grey">mdi-desk</v-icon>
                      </div>
                    </template>
                  </v-img>

                  <!-- desk label -->
                  <div class="desk-label">
                    <v-chip color="primary" size="small">{{ desk.id }}</v-chip>
                  </div>
                </div>
              </v-col>

              <!-- RIGHT SIDE -->
              <v-col cols="12" md="8">
                <v-card-text class="pa-4">
                  <!-- Booking info -->
                  <v-alert
                    color="success"
                    variant="tonal"
                    density="compact"
                    class="mb-3 d-flex flex-column align-center justify-center text-center py-4 ga-1"
                  >
                    <div class="text-subtitle-2 font-weight-bold">Active Booking</div>

                    <div class="text-caption d-flex align-center justify-center ga-1">
                      <v-icon size="x-small">mdi-calendar</v-icon>
                      {{
                        props.bookings.find(
                          (b) => b.deskId === desk.id && b.userId === props.currentUser,
                        )?.date || 'N/A'
                      }}
                    </div>

                    <div class="text-caption d-flex align-center justify-center ga-1">
                      <v-icon size="x-small">mdi-clock-outline</v-icon>
                      {{
                        props.bookings.find(
                          (b) => b.deskId === desk.id && b.userId === props.currentUser,
                        )?.startTime || 'N/A'
                      }}
                      &nbsp;–&nbsp;
                      {{
                        props.bookings.find(
                          (b) => b.deskId === desk.id && b.userId === props.currentUser,
                        )?.endTime || 'N/A'
                      }}
                    </div>
                  </v-alert>

                  <!-- Preset Height Buttons -->
                  <div class="mb-3">
                    <v-btn
                      color="primary"
                      variant="flat"
                      size="small"
                      prepend-icon="mdi-arrow-up"
                      block
                      class="mb-2"
                      :loading="loading"
                      @click="setStandingHeight"
                    >
                      Standing Height ({{ standingHeight }}mm)
                    </v-btn>
                    <v-btn
                      color="primary"
                      variant="outlined"
                      size="small"
                      prepend-icon="mdi-arrow-down"
                      block
                      :loading="loading"
                      @click="setSittingHeight"
                    >
                      Sitting Height ({{ sittingHeight }}mm)
                    </v-btn>
                  </div>

                  <!-- Current Height Display -->
                  <v-alert type="info" variant="tonal" density="compact" class="mb-3">
                    <div class="text-center">
                      <div class="text-caption">Current Height</div>
                      <div class="text-h6 font-weight-bold">{{ currentHeight }} mm</div>
                    </div>
                  </v-alert>

                  <!-- Custom Position Input -->
                  <div class="mb-3">
                    <v-text-field
                      v-model.number="customPosition"
                      label="Change Desk Position (mm)"
                      type="number"
                      variant="outlined"
                      density="compact"
                      hide-details
                      prepend-inner-icon="mdi-ruler"
                      :min="620"
                      :max="1270"
                    />
                  </div>

                  <!-- Change Position Button -->
                  <v-btn
                    color="secondary"
                    variant="flat"
                    size="small"
                    prepend-icon="mdi-swap-vertical"
                    block
                    :loading="loading"
                    :disabled="!customPosition"
                    @click="setCustomPosition"
                  >
                    Change Position
                  </v-btn>
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- Snackbar for notifications -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000" location="top">
      {{ snackbar.text }}
    </v-snackbar>
  </v-card>
</template>

<style scoped>
.booking-detail-card {
  overflow: hidden;
}

.image-wrapper {
  position: relative;
  height: 300px;
  background-color: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.desk-label {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 1;
}
</style>
