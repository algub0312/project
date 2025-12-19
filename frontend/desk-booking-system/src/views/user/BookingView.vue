<script lang="ts" setup>
import { computed, ref, watch } from 'vue'

// Composables
import { useDeskData } from '@/composables/useDeskData'
import { useFilters } from '@/composables/useFilters'
import { useBookingState } from '@/composables/booking/useBookingState.ts'
import { useBookingActions } from '@/composables/booking/useBookingActions.ts'
import { useCalendar } from '@/composables/useCalendar'
import { useBookingsQuery } from '@/queries/booking/useBookingsQuery'
import { useOccupancy } from '@/composables/useOccupancy'

// UI components
import BookingHeader from '@/components/booking/BookingHeader.vue'
import FiltersBar from '@/components/booking/FiltersBar.vue'
import DeskGrid from '@/components/booking/DeskGrid.vue'
import ContextMenuDialog from '@/components/booking/ContextMenuDialog.vue'
import BookingDialog from '@/components/booking/BookingDialog.vue'
import WeeklyAvailabilityDialog from '@/components/booking/WeeklyAvailabilityDialog.vue'
import RequireRole from '@/components/RequireRole.vue'
import BookingControlBar from '@/components/booking/BookingControlBar.vue'

import type { Booking } from '@/types/booking'
import { toDeskDrawingData } from '@/types/deskDrawingData.ts'
import type { Desk } from '@/types/desk.ts'
import { useDeskStatus } from '@/composables/booking/useDeskStatus.ts'
import { fromDeskIdToDesk } from '@/composables/booking/useDeskId.ts'

const {
  selectedStart,
  selectedEnd,
  bookingDialog,
  selectedDesk,
  contextMenu,
  contextMenuDesk,
  weeklyAvailabilityDialog,
  selectedDeskForWeekly,
} = useBookingState()

const { data, refetch } = useBookingsQuery(selectedStart, selectedEnd)
const bookings = computed<Booking[]>(() => data.value ?? [])

watch([selectedStart, selectedEnd], () => {
  refetch()
})

const {
  openBookingDialog,
  handleDeskRightClick,
  quickBookNow,
  bookHalfDay,
  bookFullDay,
  createBooking,
} = useBookingActions(
  selectedStart,
  selectedEnd,
  selectedDesk,
  bookingDialog,
  contextMenu,
  contextMenuDesk,
)

const { desks, userBookings } = useDeskData()
const selectedFloor = ref(0)

const { desksWithStatus } = useDeskStatus(desks, bookings, selectedStart, selectedEnd)

const { fetchAllOccupancy, isLoading: isLoadingOccupancy } = useOccupancy(true, 30000)

const {
  searchQuery,
  selectedStatus,
  selectedFeatures,
  availableFeatures,
  filteredDesks,
  toggleQuickFilter,
  clearFilters,
  hasActiveFilters,
} = useFilters(desksWithStatus)

const desksByFloor = computed(() => {
  return filteredDesks.value.filter((desk) => desk.floor === selectedFloor.value)
})

const { weekDays, getDeskBookingForDate } = useCalendar(userBookings)

const toggleFavorite = (desk: Desk) => {
  const idx = desks.value.findIndex((d) => d.id === desk.id)
  if (idx !== -1) desks.value[idx].isFavorite = !desks.value[idx].isFavorite
  contextMenu.value = false
}

const viewWeeklyAvailability = (desk: Desk) => {
  selectedDeskForWeekly.value = desk
  weeklyAvailabilityDialog.value = true
  contextMenu.value = false
}

const handleConfirmBooking = async () => {
  try {
    await createBooking()
    await refetch() // Refresh bookings after creation
  } catch (error) {
    console.error('Error creating booking:', error)
  }
}
</script>

<template>
  <RequireRole :roles="['user']">
    <v-container class="booking-view pa-6" fluid>
      <BookingHeader />

      <v-row class="mb-4">
        <v-col cols="12">
          <v-card class="pa-4">
            <div class="d-flex justify-space-between align-center">
              <div>
                <h3 class="text-h6">Bookings Status</h3>
                <p class="text-body-2 text-grey">Real-time occupancy for your reserved desks</p>
              </div>
              <v-btn
                icon="mdi-refresh"
                variant="text"
                :loading="isLoadingOccupancy"
                @click="fetchAllOccupancy"
              />
            </div>
          </v-card>
        </v-col>
      </v-row>

      <FiltersBar
        :available-features="availableFeatures"
        :filtered-desk-count="filteredDesks.length"
        :has-active-filters="hasActiveFilters"
        :search-query="searchQuery"
        :selected-features="selectedFeatures"
        :selected-status="selectedStatus"
        :total-desks="desks.length"
        @clear="clearFilters"
        @toggleQuick="toggleQuickFilter"
        @update:searchQuery="(val) => (searchQuery = val)"
        @update:selectedStatus="(val) => (selectedStatus = val)"
        @update:selectedFeatures="(val) => (selectedFeatures = val)"
      />

      <BookingControlBar
        :end="selectedEnd"
        :start="selectedStart"
        @update:start="selectedStart = $event"
        @update:end="selectedEnd = $event"
      />

      <v-row class="mb-4 mt-4">
        <v-col cols="12">
          <div class="d-flex ga-4">
            <div class="me-auto">
              <v-chip class="mr-2" color="success" size="small" />
              <span class="text-body-2 mr-4">Available</span>
              <v-chip color="error" size="small" class="mr-2" />
              <span class="text-body-2 mr-4">Occupied (Real-time IoT)</span>
              <v-chip class="mr-2" color="warning" size="small" />
              <span class="text-body-2 mr-4">Reserved</span>
              <v-chip class="mr-2" color="grey" size="small" />
              <span class="text-body-2 mr-4">Maintenance</span>
            </div>

            <v-btn-toggle v-model="selectedFloor" color="primary" mandatory rounded="lg">
              <v-btn :value="0">
                <v-icon start>mdi-layers</v-icon>
                Floor 0
              </v-btn>
              <v-btn :value="1">
                <v-icon start>mdi-layers</v-icon>
                Floor 1
              </v-btn>
            </v-btn-toggle>
          </div>
        </v-col>
      </v-row>

      <DeskGrid
        :drawing-data="toDeskDrawingData(desksByFloor, bookings)"
        @left="
          (deskId) => {
            const desk = fromDeskIdToDesk(deskId, desksWithStatus)
            if (desk) openBookingDialog(desk)
          }
        "
        @right="
          (deskId, ev) => {
            const desk = fromDeskIdToDesk(deskId, desksWithStatus)
            if (desk) handleDeskRightClick(desk, ev)
          }
        "
      />

      <ContextMenuDialog
        v-model="contextMenu"
        :desk="contextMenuDesk"
        @favorite="() => toggleFavorite(contextMenuDesk!)"
        @full="() => bookFullDay(contextMenuDesk!)"
        @half="() => bookHalfDay(contextMenuDesk!)"
        @quick="(h: number) => quickBookNow(contextMenuDesk!, h)"
        @weekly="() => viewWeeklyAvailability(contextMenuDesk!)"
      />

      <BookingDialog
        v-model="bookingDialog"
        :desk-id="selectedDesk?.id"
        :end="selectedEnd"
        :start="selectedStart"
        @confirm="handleConfirmBooking"
        @update:start="selectedStart = $event"
        @update:end="selectedEnd = $event"
      />

      <WeeklyAvailabilityDialog
        v-model="weeklyAvailabilityDialog"
        :desk="selectedDeskForWeekly"
        :is-booked="(deskId, date) => getDeskBookingForDate(deskId, date)"
        :week-days="weekDays"
        @book="() => selectedDesk && (bookingDialog = true)"
      />
    </v-container>
  </RequireRole>
</template>

<style scoped>
.booking-view {
  min-height: 100vh;
}
</style>
