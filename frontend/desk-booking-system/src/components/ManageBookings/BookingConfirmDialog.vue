<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: boolean
  type: 'cancel' | 'delete'
}>()

const emit = defineEmits(['update:modelValue', 'confirm'])

const config = {
  cancel: {
    title: 'Cancel Booking?',
    message: 'Are you sure you want to cancel this booking? This action can be undone.',
    confirmText: 'Yes, Cancel',
    confirmColor: 'warning',
    titleClass: 'text-h5',
  },
  delete: {
    title: 'Delete Booking?',
    message:
      'Are you sure you want to permanently delete this booking? This action cannot be undone.',
    confirmText: 'Yes, Delete',
    confirmColor: 'error',
    titleClass: 'text-h5 text-error',
  },
}

const title = computed(() => config[props.type].title)
const message = computed(() => config[props.type].message)
const confirmText = computed(() => config[props.type].confirmText)
const confirmColor = computed(() => config[props.type].confirmColor)
const titleClass = computed(() => config[props.type].titleClass)

const handleConfirm = () => {
  emit('confirm')
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="400"
  >
    <v-card>
      <v-card-title :class="titleClass">
        {{ title }}
      </v-card-title>
      <v-card-text>
        {{ message }}
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="$emit('update:modelValue', false)"> No </v-btn>
        <v-btn :color="confirmColor" variant="flat" @click="handleConfirm">
          {{ confirmText }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
