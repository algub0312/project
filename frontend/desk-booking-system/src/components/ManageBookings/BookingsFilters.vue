<script setup lang="ts">
defineProps<{
  search: string
  status: string
  dateRange: string
  customDate: string
}>()

defineEmits(['update:search', 'update:status', 'update:dateRange', 'update:customDate', 'reset'])

const statusOptions = ['All', 'Active', 'Completed', 'Cancelled']
const dateFilterOptions = ['All', 'Today', 'This Week', 'This Month', 'Past', 'Future']
</script>

<template>
  <v-row>
    <v-col cols="12" md="3">
      <v-text-field
        :model-value="search"
        @update:model-value="$emit('update:search', $event)"
        prepend-inner-icon="mdi-magnify"
        label="Search by user or desk"
        variant="outlined"
        density="comfortable"
        clearable
        hide-details
      />
    </v-col>
    <v-col cols="12" md="2">
      <v-select
        :model-value="status"
        @update:model-value="$emit('update:status', $event)"
        :items="statusOptions"
        label="Status"
        variant="outlined"
        density="comfortable"
        hide-details
      />
    </v-col>
    <v-col cols="12" md="2">
      <v-select
        :model-value="dateRange"
        @update:model-value="$emit('update:dateRange', $event)"
        :items="dateFilterOptions"
        label="Date Range"
        variant="outlined"
        density="comfortable"
        hide-details
      />
    </v-col>
    <v-col cols="12" md="3">
      <v-text-field
        :model-value="customDate"
        @update:model-value="$emit('update:customDate', $event)"
        type="date"
        label="Custom Date"
        variant="outlined"
        density="comfortable"
        hide-details
      />
    </v-col>
    <v-col cols="12" md="2">
      <v-btn color="secondary" variant="outlined" block @click="$emit('reset')">
        Reset Filters
      </v-btn>
    </v-col>
  </v-row>
</template>
