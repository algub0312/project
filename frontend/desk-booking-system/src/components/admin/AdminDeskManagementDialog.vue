<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Booking } from '@/types/mockData'
import type { Desk } from '@/types/desk.ts'
import type { DeskStatus } from '@/types/deskStatus.ts'

const props = defineProps<{
  modelValue: boolean
  desk: Desk | null
  allBookings: Booking[]
  isPhysicallyOccupied?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  updateStatus: [deskId: number, status: DeskStatus]
  updateBooking: [booking: Booking]
  deleteBooking: [bookingId: string]
}>()

const newStatus = ref<DeskStatus>('available')
const editingBooking = ref<Booking | null>(null)
const showEditBooking = ref(false)

// Get all bookings for this desk
const deskBookings = computed(() => {
  if (!props.desk) return []
  return props.allBookings
    .filter((b) => b.deskId === props.desk!.id && b.status === 'active')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const hasConflict = computed(() => {
  return props.isPhysicallyOccupied && deskBookings.value.length === 0
})

const statusItems = [
  { title: 'Available', value: 'available' },
  { title: 'Occupied', value: 'occupied' },
  { title: 'Reserved', value: 'reserved' },
  { title: 'Maintenance', value: 'maintenance' },
]

const updateStatus = () => {
  if (props.desk) {
    emit('updateStatus', props.desk.id, newStatus.value)
  }
}

const startEditBooking = (booking: Booking) => {
  editingBooking.value = { ...booking }
  showEditBooking.value = true
}

const saveBookingEdit = () => {
  if (editingBooking.value) {
    emit('updateBooking', editingBooking.value)
    showEditBooking.value = false
    editingBooking.value = null
  }
}

const deleteBooking = (bookingId: string) => {
  if (confirm('Are you sure you want to delete this booking?')) {
    emit('deleteBooking', bookingId)
  }
}

const handleDialogChange = (value: boolean) => {
  if (value && props.desk) {
    newStatus.value = props.desk.status
  }
  emit('update:modelValue', value)
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="handleDialogChange"
    max-width="700"
    scrollable
  >
    <v-card>
      <v-card-title class="text-h5 d-flex align-center justify-space-between pa-4 bg-primary">
        <div class="d-flex align-center gap-2">
          <v-icon color="white">mdi-desk</v-icon>
          <span class="text-white">Manage Desk {{ desk?.id }}</span>
        </div>
        <div class="d-flex gap-2">
          <!-- IoT Status Chip -->
          <v-chip
            v-if="isPhysicallyOccupied !== undefined"
            :color="isPhysicallyOccupied ? 'error' : 'success'"
            size="small"
            variant="flat"
          >
            <v-icon start size="small">
              {{ isPhysicallyOccupied ? 'mdi-account' : 'mdi-check-circle' }}
            </v-icon>
            {{ isPhysicallyOccupied ? 'IoT: Occupied' : 'IoT: Free' }}
          </v-chip>

          <!-- Booking Status Chip -->
          <v-chip
            :color="
              desk?.status === 'available'
                ? 'success'
                : desk?.status === 'occupied' || desk?.status === 'reserved'
                  ? 'error'
                  : 'grey'
            "
            size="small"
            variant="flat"
          >
            {{ desk?.status }}
          </v-chip>
        </div>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4" style="max-height: 600px">
        <!-- CONFLICT WARNING - Shows when desk is occupied but has no bookings -->
        <v-alert
          v-if="hasConflict"
          type="warning"
          variant="tonal"
          prominent
          border="start"
          class="mb-4"
        >
          <v-alert-title class="d-flex align-center gap-2">
            <v-icon>mdi-alert-circle</v-icon>
            <strong>Unauthorized Usage Detected</strong>
          </v-alert-title>
          <div class="mt-2">
            <strong>This desk is physically occupied but has no active bookings.</strong>
            <br />
            Someone may be using this desk without authorization. Consider investigating or updating
            the booking system.
          </div>
        </v-alert>

        <!-- REAL-TIME IoT STATUS -->
        <v-alert
          v-if="isPhysicallyOccupied !== undefined"
          :type="isPhysicallyOccupied ? 'error' : 'success'"
          variant="tonal"
          density="compact"
          class="mb-4"
        >
          <div class="d-flex align-center gap-2">
            <v-icon>{{ isPhysicallyOccupied ? 'mdi-access-point' : 'mdi-check-circle' }}</v-icon>
            <strong>Real-time IoT Sensor:</strong>
            <span>
              Desk is <strong>{{ isPhysicallyOccupied ? 'OCCUPIED' : 'AVAILABLE' }}</strong>
            </span>
          </div>
        </v-alert>

        <!-- Desk Information -->
        <v-alert type="info" variant="tonal" density="compact" class="mb-4">
          <div class="d-flex justify-space-between align-center">
            <div>
              <strong>Desk:</strong> {{ desk?.id }} | <strong>Floor:</strong> {{ desk?.floor }}
              <span v-if="desk?.features && desk.features.length > 0">
                | <strong>Features:</strong>
                <v-chip
                  v-for="feature in desk.features"
                  :key="feature"
                  size="x-small"
                  class="ml-1"
                  variant="outlined"
                >
                  {{ feature }}
                </v-chip>
              </span>
            </div>
            <v-icon v-if="desk?.isFavorite" color="red">mdi-heart</v-icon>
          </div>
        </v-alert>

        <!-- Status Comparison Card (when IoT data is available) -->
        <v-card
          v-if="isPhysicallyOccupied !== undefined"
          variant="outlined"
          class="mb-4"
          :color="hasConflict ? 'warning' : undefined"
        >
          <v-card-text>
            <h3 class="text-subtitle-1 mb-3 font-weight-bold">
              <v-icon start>mdi-compare</v-icon>
              Status Comparison
            </h3>
            <v-row dense>
              <v-col cols="6">
                <div class="text-caption text-grey mb-1">Booking System Status</div>
                <v-chip
                  :color="
                    desk?.status === 'available'
                      ? 'success'
                      : desk?.status === 'occupied' || desk?.status === 'reserved'
                        ? 'error'
                        : 'grey'
                  "
                  size="small"
                  variant="flat"
                >
                  {{ desk?.status }}
                </v-chip>
              </v-col>
              <v-col cols="6">
                <div class="text-caption text-grey mb-1">Physical IoT Sensor</div>
                <v-chip
                  :color="isPhysicallyOccupied ? 'error' : 'success'"
                  size="small"
                  variant="flat"
                >
                  <v-icon start size="small">
                    {{ isPhysicallyOccupied ? 'mdi-account' : 'mdi-check' }}
                  </v-icon>
                  {{ isPhysicallyOccupied ? 'Occupied' : 'Available' }}
                </v-chip>
              </v-col>
            </v-row>

            <!-- Show sync status -->
            <v-divider class="my-2" />
            <div class="text-caption d-flex align-center gap-1">
              <v-icon :color="!hasConflict ? 'success' : 'warning'" size="small">
                {{ !hasConflict ? 'mdi-check-circle' : 'mdi-alert-circle' }}
              </v-icon>
              <span :class="hasConflict ? 'text-warning' : 'text-success'">
                {{ !hasConflict ? 'Statuses are synchronized' : 'Status mismatch detected' }}
              </span>
            </div>
          </v-card-text>
        </v-card>

        <!-- Change Status Section -->
        <v-card variant="outlined" class="mb-4">
          <v-card-text>
            <h3 class="text-h6 mb-3">Change Desk Status</h3>
            <v-select
              v-model="newStatus"
              :items="statusItems"
              label="Desk Status"
              variant="outlined"
              density="comfortable"
              hide-details
              class="mb-3"
            />
            <v-btn
              color="primary"
              variant="flat"
              block
              @click="updateStatus"
              :disabled="newStatus === desk?.status"
            >
              <v-icon start>mdi-content-save</v-icon>
              Update Status
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Current Bookings Section -->
        <v-card variant="outlined">
          <v-card-text>
            <div class="d-flex align-center justify-space-between mb-3">
              <h3 class="text-h6">Active Bookings ({{ deskBookings.length }})</h3>
              <v-chip size="small" :color="deskBookings.length > 0 ? 'error' : 'success'">
                {{ deskBookings.length > 0 ? 'Has Bookings' : 'No Bookings' }}
              </v-chip>
            </div>

            <div v-if="deskBookings.length === 0" class="text-center text-grey py-4">
              <v-icon size="64" color="grey-lighten-1">mdi-calendar-blank</v-icon>
              <div class="text-body-2 mt-2">No active bookings for this desk</div>
            </div>

            <v-list v-else density="compact">
              <v-list-item
                v-for="booking in deskBookings"
                :key="booking.id"
                class="mb-2 booking-item"
                border
                rounded
              >
                <template #prepend>
                  <v-avatar color="primary" size="40">
                    <v-icon>mdi-calendar-clock</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="font-weight-bold">
                  {{
                    new Date(booking.date).toLocaleDateString('en-GB', {
                      weekday: 'short',
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })
                  }}
                </v-list-item-title>

                <v-list-item-subtitle>
                  <v-icon size="small">mdi-clock-outline</v-icon>
                  {{ booking.startTime }} - {{ booking.endTime }}
                  <br />
                  <v-icon size="small">mdi-account</v-icon>
                  User: {{ booking.userId }}
                  <span v-if="booking.notes">
                    <br />
                    <v-icon size="small">mdi-note-text</v-icon>
                    {{ booking.notes }}
                  </span>
                </v-list-item-subtitle>

                <template #append>
                  <div class="d-flex flex-column ga-1">
                    <v-btn
                      icon="mdi-pencil"
                      size="small"
                      variant="text"
                      color="primary"
                      @click="startEditBooking(booking)"
                    />
                    <v-btn
                      icon="mdi-delete"
                      size="small"
                      variant="text"
                      color="error"
                      @click="deleteBooking(booking.id)"
                    />
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="grey" variant="text" @click="emit('update:modelValue', false)">
          <v-icon start>mdi-close</v-icon>
          Close
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Edit Booking Dialog -->
    <v-dialog v-model="showEditBooking" max-width="500">
      <v-card v-if="editingBooking">
        <v-card-title class="text-h6 bg-primary text-white">
          <v-icon start color="white">mdi-pencil</v-icon>
          Edit Booking
        </v-card-title>
        <v-card-text class="pt-4">
          <v-alert type="warning" variant="tonal" density="compact" class="mb-4">
            Editing booking for <strong>{{ editingBooking.userId }}</strong>
          </v-alert>

          <v-text-field
            v-model="editingBooking.date"
            label="Date"
            type="date"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            prepend-inner-icon="mdi-calendar"
          />

          <v-text-field
            v-model="editingBooking.startTime"
            label="Start Time"
            type="time"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            prepend-inner-icon="mdi-clock-start"
          />

          <v-text-field
            v-model="editingBooking.endTime"
            label="End Time"
            type="time"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            prepend-inner-icon="mdi-clock-end"
          />

          <v-textarea
            v-model="editingBooking.notes"
            label="Notes (Optional)"
            variant="outlined"
            density="comfortable"
            rows="2"
            prepend-inner-icon="mdi-note-text"
          />
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn color="grey" variant="text" @click="showEditBooking = false">
            <v-icon start>mdi-close</v-icon>
            Cancel
          </v-btn>
          <v-btn color="primary" variant="flat" @click="saveBookingEdit">
            <v-icon start>mdi-content-save</v-icon>
            Save Changes
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<style scoped>
.booking-item {
  transition: all 0.2s;
}

.booking-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}
</style>
