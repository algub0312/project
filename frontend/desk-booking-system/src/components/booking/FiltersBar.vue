<script setup lang="ts">
const props = defineProps<{
  searchQuery: string
  selectedStatus: string[]
  selectedFeatures: string[]
  availableFeatures: { value: string; label: string; icon: string }[]
  hasActiveFilters: boolean
  totalDesks: number
  filteredDeskCount: number
}>()

const emits = defineEmits<{
  (e: 'update:searchQuery', v: string): void
  (e: 'update:selectedStatus', v: string[]): void
  (e: 'update:selectedFeatures', v: string[]): void
  (e: 'toggleQuick', v: string): void
  (e: 'clear'): void
}>()
</script>

<template>
  <v-card elevation="2" class="pa-4 mb-4">
    <v-row>
      <v-col cols="12" md="4">
        <v-text-field
          :model-value="props.searchQuery"
          @update:model-value="emits('update:searchQuery', $event)"
          label="Search by desk number"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          hide-details
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          :model-value="props.selectedStatus"
          @update:model-value="emits('update:selectedStatus', $event)"
          :items="[
            { value: 'available', title: 'Available' },
            { value: 'occupied', title: 'Occupied' },
            { value: 'reserved', title: 'Reserved' },
            { value: 'maintenance', title: 'Maintenance' },
          ]"
          label="Filter by status"
          prepend-inner-icon="mdi-filter"
          variant="outlined"
          density="compact"
          multiple
          chips
          closable-chips
          hide-details
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          :model-value="props.selectedFeatures"
          @update:model-value="emits('update:selectedFeatures', $event)"
          :items="props.availableFeatures"
          item-title="label"
          item-value="value"
          label="Filter by features"
          prepend-inner-icon="mdi-star"
          variant="outlined"
          density="compact"
          multiple
          chips
          closable-chips
          hide-details
        >
          <template #chip="{ item, props }">
            <v-chip v-bind="props">
              <v-icon start :icon="availableFeatures.find((f) => f.value === item.value)?.icon" />
              {{ item.title }}
            </v-chip>
          </template>
        </v-select>
      </v-col>
    </v-row>

    <v-row class="mt-2">
      <v-col cols="12">
        <div class="d-flex flex-wrap ga-2 align-center">
          <span class="text-body-2 text-grey-darken-1 mr-2">Quick Filters:</span>
          <v-chip variant="outlined" @click="emits('toggleQuick', 'available-now')" clickable>
            <v-icon start>mdi-check-circle</v-icon> Available Now
          </v-chip>
          <v-chip variant="outlined" @click="emits('toggleQuick', 'available-today')" clickable>
            <v-icon start>mdi-calendar-today</v-icon> Available Today
          </v-chip>
          <v-chip variant="outlined" @click="emits('toggleQuick', 'my-bookings')" clickable>
            <v-icon start>mdi-account</v-icon> My Bookings
          </v-chip>
          <v-chip variant="outlined" @click="emits('toggleQuick', 'favorites')" clickable>
            <v-icon start>mdi-heart</v-icon> Favorites
          </v-chip>

          <v-btn
            v-if="props.hasActiveFilters"
            color="error"
            variant="text"
            size="small"
            class="ml-2"
            @click="emits('clear')"
          >
            <v-icon start>mdi-close</v-icon> Clear All
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-row v-if="props.hasActiveFilters" class="mt-2">
      <v-col cols="12">
        <v-alert type="info" variant="tonal" density="compact">
          Showing {{ props.filteredDeskCount }} of {{ props.totalDesks }} desks
        </v-alert>
      </v-col>
    </v-row>
  </v-card>
</template>
