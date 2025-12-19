<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const SITTING_MULTIPLIER = 0.45
const STANDING_MULTIPLIER = 0.7

const props = defineProps<{
  initialHeight?: number
  initialSittingHeight?: number
  initialStandingHeight?: number
}>()

const emit = defineEmits<{
  (e: 'save', data: { userHeight: number; sittingHeight: number; standingHeight: number }): void
}>()

const heightCm = ref<number | null>(props.initialHeight ?? null)
const isEditMode = ref(false)
const isSaving = ref(false)

const sittingHeight = ref<number | null>(props.initialSittingHeight ?? null)
const standingHeight = ref<number | null>(props.initialStandingHeight ?? null)

watch(heightCm, (newHeight) => {
  if (newHeight && newHeight > 0 && !isEditMode.value) {
    sittingHeight.value = Math.round(newHeight * SITTING_MULTIPLIER)
    standingHeight.value = Math.round(newHeight * STANDING_MULTIPLIER)
  }
})

const isValidInput = computed(() => {
  return heightCm.value && heightCm.value > 0
})

const canSave = computed(() => {
  return (
    isValidInput.value &&
    sittingHeight.value &&
    sittingHeight.value > 0 &&
    standingHeight.value &&
    standingHeight.value > 0
  )
})

const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value
}

const handleSave = async () => {
  if (!canSave.value) return

  isSaving.value = true

  try {
    emit('save', {
      userHeight: heightCm.value!,
      sittingHeight: sittingHeight.value!,
      standingHeight: standingHeight.value!,
    })
    isEditMode.value = false
  } catch (error) {
    console.error('Error saving desk preferences:', error)
  } finally {
    isSaving.value = false
  }
}

const reset = () => {
  heightCm.value = null
  sittingHeight.value = null
  standingHeight.value = null
  isEditMode.value = false
}
</script>

<template>
  <v-card class="mx-auto" max-width="600">
    <v-card-title class="text-h6 font-weight-bold">
      <v-icon start>mdi-desk</v-icon>
      Desk Height Calculator
    </v-card-title>

    <v-card-subtitle>
      Enter your height to calculate the ideal desk heights for ergonomic comfort.
    </v-card-subtitle>

    <v-card-text>
      <!-- Height Input -->
      <v-row class="mb-4">
        <v-col cols="12">
          <v-text-field
            v-model.number="heightCm"
            label="Your Height"
            type="number"
            variant="outlined"
            density="comfortable"
            suffix="cm"
            :rules="[(v) => !!v || 'Height is required', (v) => v > 0 || 'Height must be positive']"
            hint="Enter your height in centimeters"
            persistent-hint
          />
        </v-col>
      </v-row>

      <!-- Results Display -->
      <v-expand-transition>
        <div v-if="isValidInput">
          <v-divider class="mb-4" />

          <div class="d-flex justify-space-between align-center mb-3">
            <h3 class="text-h6">Recommended Heights</h3>
            <v-btn
              :color="isEditMode ? 'primary' : 'secondary'"
              :variant="isEditMode ? 'flat' : 'outlined'"
              size="small"
              @click="toggleEditMode"
            >
              <v-icon start>{{ isEditMode ? 'mdi-check' : 'mdi-pencil' }}</v-icon>
              {{ isEditMode ? 'Done Editing' : 'Edit' }}
            </v-btn>
          </div>

          <!-- Sitting Height -->
          <v-row class="mb-2">
            <v-col cols="12">
              <v-card variant="tonal" color="info">
                <v-card-text>
                  <div class="d-flex justify-space-between align-center">
                    <div>
                      <div class="text-overline">Sitting Desk Height</div>
                      <div v-if="!isEditMode" class="text-h5 font-weight-bold">
                        {{ sittingHeight }} cm
                      </div>
                    </div>
                    <v-icon size="40" color="info">mdi-chair-rolling</v-icon>
                  </div>
                  <v-text-field
                    v-if="isEditMode"
                    v-model.number="sittingHeight"
                    type="number"
                    variant="outlined"
                    density="compact"
                    suffix="cm"
                    class="mt-2"
                    :rules="[(v) => !!v || 'Required', (v) => v > 0 || 'Must be positive']"
                  />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Standing Height -->
          <v-row class="mb-4">
            <v-col cols="12">
              <v-card variant="tonal" color="success">
                <v-card-text>
                  <div class="d-flex justify-space-between align-center">
                    <div>
                      <div class="text-overline">Standing Desk Height</div>
                      <div v-if="!isEditMode" class="text-h5 font-weight-bold">
                        {{ standingHeight }} cm
                      </div>
                    </div>
                    <v-icon size="40" color="success">mdi-human-handsup</v-icon>
                  </div>
                  <v-text-field
                    v-if="isEditMode"
                    v-model.number="standingHeight"
                    type="number"
                    variant="outlined"
                    density="compact"
                    suffix="cm"
                    class="mt-2"
                    :rules="[(v) => !!v || 'Required', (v) => v > 0 || 'Must be positive']"
                  />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Info Alert -->
          <v-alert type="info" variant="tonal" density="compact" class="mb-3">
            <div class="text-caption">
              <strong>Tip:</strong> These heights ensure your elbows are at a 90° angle when typing.
              Adjust as needed for your comfort.
            </div>
          </v-alert>
        </div>
      </v-expand-transition>
    </v-card-text>

    <v-card-actions>
      <v-btn v-if="isValidInput" color="secondary" variant="outlined" @click="reset"> Reset </v-btn>
      <v-spacer />
      <v-btn
        color="primary"
        variant="elevated"
        :disabled="!canSave"
        :loading="isSaving"
        @click="handleSave"
      >
        <v-icon start>mdi-content-save</v-icon>
        Save Preferences
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.text-overline {
  line-height: 1;
  margin-bottom: 4px;
}
</style>
