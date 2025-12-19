<script setup lang="ts">
import { useBookingsAdmin } from '@/composables/useBookingAdmin'
import BookingsFilters from '@/components/ManageBookings/BookingsFilters.vue'
import BookingsTable from '@/components/ManageBookings/BookingsTable.vue'
import BookingDetailsDialog from '@/components/ManageBookings/BookingDetailsDialog.vue'
import BookingEditDialog from '@/components/ManageBookings/BookingEditDialog.vue'
import BookingConfirmDialog from '@/components/ManageBookings/BookingConfirmDialog.vue'
import RequireRole from '@/components/RequireRole.vue'

const {
  bookings,
  loading,
  filteredBookings,
  filters,
  dialogs,
  selectedBooking,
  editingBooking,
  snackbar,
  resetFilters,
  handleView,
  handleEdit,
  handleSave,
  handleCancel,
  confirmCancel,
  handleDelete,
  confirmDelete,
} = useBookingsAdmin()
</script>

<template>
  <RequireRole :roles="['admin']">
    <v-container fluid class="pa-6">
      <!-- Header -->
      <v-row class="mb-6">
        <v-col>
          <h1 class="text-h4 font-weight-bold">Manage Bookings</h1>
          <p class="text-body-1 text-medium-emphasis mt-2">
            View, edit, and manage all desk bookings
          </p>
        </v-col>
      </v-row>

      <!-- Filters -->
      <BookingsFilters
        :search="filters.search"
        :status="filters.status"
        :dateRange="filters.dateRange"
        :customDate="filters.customDate"
        @update:search="filters.search = $event"
        @update:status="filters.status = $event"
        @update:dateRange="filters.dateRange = $event"
        @update:customDate="filters.customDate = $event"
        @reset="resetFilters"
      />

      <!-- Stats -->
      <v-row class="mt-4">
        <v-col cols="12" md="3">
          <v-card elevation="2">
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon size="40" color="primary" class="mr-3">mdi-calendar-check</v-icon>
                <div>
                  <div class="text-h5 font-weight-bold">{{ bookings.length }}</div>
                  <div class="text-caption text-medium-emphasis">Total Bookings</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card elevation="2">
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon size="40" color="success" class="mr-3">mdi-check-circle</v-icon>
                <div>
                  <div class="text-h5 font-weight-bold">
                    {{ bookings.filter((b) => b.status === 'active').length }}
                  </div>
                  <div class="text-caption text-medium-emphasis">Active</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card elevation="2">
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon size="40" color="info" class="mr-3">mdi-check-all</v-icon>
                <div>
                  <div class="text-h5 font-weight-bold">
                    {{ bookings.filter((b) => b.status === 'completed').length }}
                  </div>
                  <div class="text-caption text-medium-emphasis">Completed</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card elevation="2">
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon size="40" color="error" class="mr-3">mdi-close-circle</v-icon>
                <div>
                  <div class="text-h5 font-weight-bold">
                    {{ bookings.filter((b) => b.status === 'cancelled').length }}
                  </div>
                  <div class="text-caption text-medium-emphasis">Cancelled</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Bookings Table -->
      <BookingsTable
        :bookings="filteredBookings"
        :loading="loading"
        @view="handleView"
        @edit="handleEdit"
        @cancel="handleCancel"
        @delete="handleDelete"
      />

      <!-- Details Dialog -->
      <BookingDetailsDialog v-model="dialogs.details" :booking="selectedBooking" />

      <!-- Edit Dialog -->
      <BookingEditDialog v-model="dialogs.edit" :booking="editingBooking" @save="handleSave" />

      <!-- Cancel Confirmation Dialog -->
      <BookingConfirmDialog v-model="dialogs.cancel" type="cancel" @confirm="confirmCancel" />

      <!-- Delete Confirmation Dialog -->
      <BookingConfirmDialog v-model="dialogs.delete" type="delete" @confirm="confirmDelete" />

      <!-- Snackbar -->
      <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        :timeout="3000"
        location="top right"
      >
        {{ snackbar.text }}
      </v-snackbar>
    </v-container>
  </RequireRole>
</template>
