<!-- src/views/MyBookingsView.vue -->
<script setup lang="ts">
import { ref } from 'vue'

// Composables
import { useDeskData } from '@/composables/useDeskData'
import { useBookingLogic } from '@/composables/useBookingLogic'
import { useCalendar } from '@/composables/useCalendar'

// UI components
import MyBookingsList from '@/components/booking/MyBookingsList.vue'
import CalendarDialog from '@/components/booking/CalendarDialog.vue'
import ContextMenuDialog from '@/components/booking/ContextMenuDialog.vue'
import BookingDialog from '@/components/booking/BookingDialog.vue'
import WeeklyAvailabilityDialog from '@/components/booking/WeeklyAvailabilityDialog.vue'
import RequireRole from '@/components/RequireRole.vue'

/* Data */
const { CURRENT_USER, desks, userBookings } = useDeskData()

/* Booking logic + context menu */
const {
  contextMenu,
  contextMenuDesk,
  bookingDialog,
  selectedDesk,
  bookingDate,
  startTime,
  endTime,
  weeklyAvailabilityDialog,
  selectedDeskForWeekly,
  quickBook,
  bookHalfDay,
  bookFullDay,
  toggleFavorite,
  confirmBooking,
  cancelBooking,
  viewWeeklyAvailability,
} = useBookingLogic(desks, userBookings, CURRENT_USER)

/* Calendar */
const { weekDays, getDeskBookingForDate } = useCalendar(userBookings)
const calendarDialog = ref(false)

/* Open calendar */
const openCalendar = () => {
  calendarDialog.value = true
}
</script>

<template>
  <RequireRole :roles="['user']">
    <v-container fluid class="my-bookings-view pa-6">
      <!-- Page Header -->
      <v-row class="mb-6">
        <v-col cols="12">
          <div>
            <h1 class="text-h4 font-weight-bold">My Bookings</h1>
            <p class="text-body-1 text-medium-emphasis mt-2">
              View and manage your desk reservations
            </p>
          </div>
        </v-col>
      </v-row>

      <!-- My Bookings List -->
      <MyBookingsList
        :desks="desks"
        :bookings="userBookings"
        :current-user="CURRENT_USER"
        @cancel="cancelBooking"
      />

      <!-- View Calendar Button -->
      <v-row class="mt-6">
        <v-col cols="12" class="d-flex justify-center">
          <v-btn color="primary" size="large" prepend-icon="mdi-calendar" @click="openCalendar">
            View Calendar
          </v-btn>
        </v-col>
      </v-row>

      <!-- Context menu dialog -->
      <ContextMenuDialog
        v-model="contextMenu"
        :desk="contextMenuDesk"
        @quick="(h: number) => quickBook(contextMenuDesk!, h)"
        @half="() => bookHalfDay(contextMenuDesk!)"
        @full="() => bookFullDay(contextMenuDesk!)"
        @favorite="() => toggleFavorite(contextMenuDesk!)"
        @weekly="() => viewWeeklyAvailability(contextMenuDesk!)"
      />

      <!-- Booking dialog -->
      <BookingDialog
        v-model="bookingDialog"
        :desk-id="selectedDesk?.id"
        :date="bookingDate"
        :start-time="startTime"
        :end-time="endTime"
        @update:date="(v) => (bookingDate = v)"
        @update:startTime="(v) => (startTime = v)"
        @update:endTime="(v) => (endTime = v)"
        @confirm="confirmBooking"
      />

      <!-- Calendar Dialog -->
      <CalendarDialog v-model="calendarDialog" :week-days="weekDays" :bookings="userBookings" />

      <!-- Weekly availability dialog -->
      <WeeklyAvailabilityDialog
        v-model="weeklyAvailabilityDialog"
        :desk="selectedDeskForWeekly"
        :week-days="weekDays"
        :is-booked="(deskId, date) => getDeskBookingForDate(deskId, date)"
        @book="
          () => {
            selectedDesk && (bookingDialog = true)
          }
        "
      />
    </v-container>
  </RequireRole>
</template>

<style scoped>
.my-bookings-view {
  min-height: 100vh;
}
</style>
