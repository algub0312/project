<!-- src/views/DeskAvailabilityView.vue -->
<script setup lang="ts">
import { computed } from 'vue'

// Composables
import { useDeskData } from '@/composables/useDeskData'
import { useAdminDeskManagement } from '@/composables/useAdminDeskManagement'
import { useOccupancy } from '@/composables/useOccupancy'

// UI Components
import AdminDeskStats from '@/components/admin/AdminDeskStats.vue'
import AdminFiltersBar from '@/components/admin/AdminFiltersBar.vue'
import AdminDeskManagementDialog from '@/components/admin/AdminDeskManagementDialog.vue'
import RequireRole from '@/components/RequireRole.vue'

/* Desk Data */
const { desks, userBookings } = useDeskData()

/* Occupancy Data - Real-time from IoT sensors */
const {
  isDeskOccupied,
  fetchAllOccupancy,
  isLoading: isLoadingOccupancy,
  getOccupiedDesks,
  getAvailableDesks,
} = useOccupancy(true, 30000) // Auto-refresh every 30 seconds

/* Admin Management Logic */
const {
  selectedFloor,
  statusFilter,
  desksByFloor,
  stats,
  managementDialog,
  selectedDesk,
  getDeskColor,
  handleDeskClick,
  handleDeskRightClick,
  updateDeskStatus,
  updateBooking,
  deleteBooking,
} = useAdminDeskManagement(desks, userBookings)

/* Enhanced desk color - combines booking status with real-time occupancy */
const getEnhancedDeskColor = (desk: any) => {
  // PRIORITY 1: Physical occupancy (from IoT sensors)
  if (isDeskOccupied(desk.id)) {
    return 'error' // Red for physically occupied
  }

  // PRIORITY 2: Maintenance status
  if (desk.status === 'maintenance') {
    return 'grey'
  }

  // PRIORITY 3: Booking status
  return getDeskColor(desk.status)
}

/* Enhanced statistics with real-time occupancy */
const enhancedStats = computed(() => {
  const occupiedDesks = getOccupiedDesks()
  const availableDesks = getAvailableDesks()

  return {
    ...stats.value,
    physicallyOccupied: occupiedDesks.length,
    physicallyAvailable: availableDesks.length,
    sensorCoverage: Math.round(
      ((occupiedDesks.length + availableDesks.length) / desks.value.length) * 100,
    ),
  }
})

/* Desk info with occupancy status */
const getDeskInfo = (desk: any) => {
  const isPhysicallyOccupied = isDeskOccupied(desk.id)
  const bookingStatus = desk.status

  return {
    id: desk.id,
    physicalStatus: isPhysicallyOccupied ? 'occupied' : 'available',
    bookingStatus: bookingStatus,
    hasConflict: bookingStatus === 'available' && isPhysicallyOccupied, // Someone is using an unbooked desk
  }
}
</script>

<template>
  <RequireRole :roles="['admin']">
    <v-container fluid class="desk-availability-view pa-6">
      <!-- Header -->
      <v-row class="mb-6">
        <v-col cols="12">
          <div class="d-flex justify-space-between align-center">
            <div>
              <h1 class="text-h4 font-weight-bold">Desk Availability Management</h1>
              <p class="text-body-1 text-medium-emphasis mt-2">
                Monitor and control desk availability across all floors with real-time IoT data
              </p>
            </div>
            <v-btn
              icon="mdi-refresh"
              variant="tonal"
              color="primary"
              :loading="isLoadingOccupancy"
              @click="fetchAllOccupancy"
              size="large"
            >
              <v-icon>mdi-refresh</v-icon>
              <v-tooltip activator="parent" location="bottom"> Refresh occupancy data </v-tooltip>
            </v-btn>
          </div>
        </v-col>
      </v-row>

      <!-- Statistics Cards -->
      <AdminDeskStats :stats="stats" />

      <!-- Filters and Floor Selector -->
      <AdminFiltersBar
        :status-filter="statusFilter"
        :selected-floor="selectedFloor"
        @update:status-filter="(val) => (statusFilter = val)"
        @update:selected-floor="(val) => (selectedFloor = val)"
      />

      <!-- Enhanced Legend -->
      <v-row class="mb-4">
        <v-col cols="12">
          <v-alert type="info" variant="tonal" density="compact">
            <div class="d-flex flex-column gap-3">
              <span class="text-body-2 font-weight-bold">
                Click any desk to manage status and bookings
              </span>
              <div class="d-flex flex-wrap ga-4">
                <div class="d-flex align-center">
                  <v-chip color="success" size="small" class="mr-2" />
                  <span class="text-body-2">Available</span>
                </div>
                <div class="d-flex align-center">
                  <v-chip color="error" size="small" class="mr-2" />
                  <span class="text-body-2">Occupied (Real-time IoT)</span>
                </div>
                <div class="d-flex align-center">
                  <v-chip color="warning" size="small" class="mr-2" />
                  <span class="text-body-2">Reserved (Booking)</span>
                </div>
                <div class="d-flex align-center">
                  <v-chip color="grey" size="small" class="mr-2" />
                  <span class="text-body-2">Maintenance</span>
                </div>
              </div>
            </div>
          </v-alert>
        </v-col>
      </v-row>

      <!-- Admin Desk Grid -->
      <v-card elevation="2" class="pa-6">
        <v-row class="mb-4">
          <v-col>
            <div class="d-flex justify-space-between align-center">
              <div>
                <h2 class="text-h5 font-weight-bold">Desk Map - Floor {{ selectedFloor }}</h2>
                <p class="text-caption text-grey mt-1">
                  Click any desk to manage • Real-time occupancy updates every 30s
                </p>
              </div>
              <v-chip :color="isLoadingOccupancy ? 'warning' : 'success'" variant="tonal">
                <v-progress-circular
                  v-if="isLoadingOccupancy"
                  indeterminate
                  size="16"
                  width="2"
                  class="mr-2"
                />
                <v-icon v-else start size="small">mdi-check-circle</v-icon>
                {{ isLoadingOccupancy ? 'Updating...' : 'Live Data' }}
              </v-chip>
            </div>
          </v-col>
        </v-row>

        <div class="desk-grid">
          <v-btn
            v-for="desk in desksByFloor"
            :key="desk.id"
            :color="getEnhancedDeskColor(desk)"
            variant="flat"
            size="large"
            class="desk-button"
            :class="{ 'desk-conflict': getDeskInfo(desk).hasConflict }"
            @click="handleDeskClick(desk)"
            @contextmenu.prevent="handleDeskRightClick($event, desk)"
          >
            <div class="desk-content">
              <!-- Conflict indicator -->
              <v-icon
                v-if="getDeskInfo(desk).hasConflict"
                size="x-small"
                color="error"
                class="conflict-icon"
              >
                mdi-alert-circle
              </v-icon>

              <!-- Desk ID -->
              <div class="d-flex align-center gap-1">
                <v-icon v-if="desk.isFavorite" size="x-small" color="red">mdi-heart</v-icon>
                <span>{{ desk.id }}</span>
              </div>

              <!-- Features -->
              <div v-if="desk.features.length" class="desk-features">
                <v-icon
                  v-for="f in desk.features"
                  :key="f"
                  size="x-small"
                  :icon="f === 'near-window' ? 'mdi-window-closed-variant' : 'mdi-monitor-multiple'"
                />
              </div>
            </div>
          </v-btn>
        </div>
      </v-card>

      <!-- Admin Management Dialog -->
      <AdminDeskManagementDialog
        v-model="managementDialog"
        :desk="selectedDesk"
        :all-bookings="userBookings"
        :is-physically-occupied="selectedDesk ? isDeskOccupied(selectedDesk.id) : undefined"
        @update-status="updateDeskStatus"
        @update-booking="updateBooking"
        @delete-booking="deleteBooking"
      />
    </v-container>
  </RequireRole>
</template>

<style scoped>
.desk-availability-view {
  min-height: 100vh;
}

.desk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}

.desk-button {
  aspect-ratio: 1;
  font-size: 0.75rem;
  font-weight: 600;
  position: relative;
  transition: all 0.3s ease;
}

.desk-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.desk-conflict {
  animation: pulse-warning 2s ease-in-out infinite;
  border: 2px solid #ff9800 !important;
}

@keyframes pulse-warning {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.7);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(255, 152, 0, 0);
  }
}

.desk-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.conflict-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

.status-indicator {
  position: absolute;
  top: 4px;
  left: 4px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  padding: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.desk-features {
  display: flex;
  gap: 2px;
  margin-top: 2px;
}

@media (max-width: 600px) {
  .desk-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
    gap: 8px;
  }
  .desk-button {
    font-size: 0.65rem;
  }
}
</style>
