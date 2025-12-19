<script setup lang="ts">
import { useDeskData } from '@/composables/useDeskData'
import { useAdminDeskManagement } from '@/composables/useAdminDeskManagement'
import { schedulerService } from '@/services/api/schedulerService.ts'
import { ref, onMounted } from 'vue'
import RequireRole from '@/components/RequireRole.vue'

const { desks, userBookings } = useDeskData()
const { desksByFloor } = useAdminDeskManagement(desks, userBookings)

// Immediate height change
const deskHeight = ref(100)
const changeHeightFeedbackMessage = ref('')
const changeHeightFeedbackVisible = ref(false)
const changeHeightFeedbackType = ref<'success' | 'error' | 'info' | 'warning'>('success')
const isChangingHeight = ref(false)

// Schedule creation
const scheduleName = ref('')
const scheduleAction = ref<'raise' | 'lower'>('raise')
const scheduleHeight = ref(100)
const scheduleHour = ref(9)
const scheduleMinute = ref(0)
const scheduleDayOfWeek = ref('*')
const scheduleId = ref('')
const scheduleFeedbackMessage = ref('')
const scheduleFeedbackVisible = ref(false)
const scheduleFeedbackType = ref<'success' | 'error' | 'info' | 'warning'>('success')
const isCreatingSchedule = ref(false)

// Schedule management
const schedules = ref<any[]>([])
const isLoadingSchedules = ref(false)
const scheduleTab = ref('create')

// Edit dialog
const editDialog = ref(false)
const editingSchedule = ref<any>(null)

const dayOfWeekOptions = [
  { title: 'Every Day', value: '*' },
  { title: 'Weekdays (Mon-Fri)', value: 'mon-fri' },
  { title: 'Weekends (Sat-Sun)', value: 'sat-sun' },
  { title: 'Monday', value: 'mon' },
  { title: 'Tuesday', value: 'tue' },
  { title: 'Wednesday', value: 'wed' },
  { title: 'Thursday', value: 'thu' },
  { title: 'Friday', value: 'fri' },
  { title: 'Saturday', value: 'sat' },
  { title: 'Sunday', value: 'sun' },
]

const changeHeightForAllDesks = async () => {
  changeHeightFeedbackVisible.value = false
  isChangingHeight.value = true

  if (deskHeight.value < 68 || deskHeight.value > 120) {
    changeHeightFeedbackMessage.value =
      'Invalid height! Please enter a value between 68 and 120 cm.'
    changeHeightFeedbackType.value = 'error'
    changeHeightFeedbackVisible.value = true
    isChangingHeight.value = false
    setTimeout(() => (changeHeightFeedbackVisible.value = false), 3000)
    return
  }

  try {
    const positionMm = deskHeight.value * 10
    console.log(`Setting all desks to ${deskHeight.value} cm (${positionMm} mm)`)
    const results = await schedulerService.setAllDesksPosition(positionMm)

    const successCount = results.filter((r: any) => r.success).length
    const totalCount = results.length

    desksByFloor.value.forEach((desk) => {
      desk.height = deskHeight.value
    })

    changeHeightFeedbackMessage.value = `Successfully set ${successCount}/${totalCount} desks to ${deskHeight.value} cm (${positionMm} mm).`
    changeHeightFeedbackType.value = successCount === totalCount ? 'success' : 'warning'
    changeHeightFeedbackVisible.value = true
    setTimeout(() => (changeHeightFeedbackVisible.value = false), 5000)
  } catch (error: any) {
    console.error('Error changing desk heights:', error)
    changeHeightFeedbackMessage.value =
      error.response?.data?.detail ||
      'Failed to change desk heights. Please check if the scheduler service is running.'
    changeHeightFeedbackType.value = 'error'
    changeHeightFeedbackVisible.value = true
    setTimeout(() => (changeHeightFeedbackVisible.value = false), 5000)
  } finally {
    isChangingHeight.value = false
  }
}

const createSchedule = async () => {
  scheduleFeedbackVisible.value = false
  isCreatingSchedule.value = true

  // Validation
  if (!scheduleName.value.trim()) {
    scheduleFeedbackMessage.value = 'Please enter a schedule name.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    isCreatingSchedule.value = false
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
    return
  }

  if (scheduleHeight.value < 68 || scheduleHeight.value > 120) {
    scheduleFeedbackMessage.value = 'Invalid height! Please enter a value between 68 and 120 cm.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    isCreatingSchedule.value = false
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
    return
  }

  if (scheduleHour.value < 0 || scheduleHour.value > 23) {
    scheduleFeedbackMessage.value = 'Hour must be between 0 and 23.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    isCreatingSchedule.value = false
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
    return
  }

  if (scheduleMinute.value < 0 || scheduleMinute.value > 59) {
    scheduleFeedbackMessage.value = 'Minute must be between 0 and 59.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    isCreatingSchedule.value = false
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
    return
  }

  try {
    const positionMm = scheduleHeight.value * 10

    const scheduleData = {
      name: scheduleName.value,
      action: scheduleAction.value,
      position_mm: positionMm,
      cron: {
        hour: scheduleHour.value,
        minute: scheduleMinute.value,
        day_of_week: scheduleDayOfWeek.value,
      },
      ...(scheduleId.value && { id: scheduleId.value }),
    }

    console.log('Creating schedule:', scheduleData)
    const result = await schedulerService.createSchedule(scheduleData)

    scheduleFeedbackMessage.value = `Schedule "${scheduleName.value}" created successfully! Next run: ${result.next_run || 'N/A'}`
    scheduleFeedbackType.value = 'success'
    scheduleFeedbackVisible.value = true

    // Reset form
    scheduleName.value = ''
    scheduleId.value = ''
    scheduleHeight.value = 100
    scheduleHour.value = 9
    scheduleMinute.value = 0
    scheduleDayOfWeek.value = '*'

    // Refresh schedules list
    await loadSchedules()

    setTimeout(() => (scheduleFeedbackVisible.value = false), 5000)
  } catch (error: any) {
    console.error('Error creating schedule:', error)
    scheduleFeedbackMessage.value =
      error.response?.data?.detail || 'Failed to create schedule. Please try again.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 5000)
  } finally {
    isCreatingSchedule.value = false
  }
}

const loadSchedules = async () => {
  isLoadingSchedules.value = true
  try {
    schedules.value = await schedulerService.getSchedules()
    console.log('Loaded schedules:', schedules.value)
  } catch (error: any) {
    console.error('Error loading schedules:', error)
    scheduleFeedbackMessage.value = 'Failed to load schedules.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
  } finally {
    isLoadingSchedules.value = false
  }
}

const deleteSchedule = async (jobId: string, scheduleName: string) => {
  if (!confirm(`Are you sure you want to delete the schedule "${scheduleName}"?`)) {
    return
  }

  try {
    await schedulerService.deleteSchedule(jobId)
    scheduleFeedbackMessage.value = `Schedule "${scheduleName}" deleted successfully.`
    scheduleFeedbackType.value = 'success'
    scheduleFeedbackVisible.value = true
    await loadSchedules()
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
  } catch (error: any) {
    console.error('Error deleting schedule:', error)
    scheduleFeedbackMessage.value = error.response?.data?.detail || 'Failed to delete schedule.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
  }
}

const openEditDialog = (schedule: any) => {
  // Parse the trigger string to extract hour, minute, day_of_week
  // Format: "cron[day_of_week='*', hour='20', minute='0']"
  const triggerMatch = schedule.trigger.match(/day_of_week='([^']*)'.*hour='(\d+)'.*minute='(\d+)'/)

  editingSchedule.value = {
    id: schedule.id,
    name: schedule.name,
    height: 100, // Default in cm
    hour: triggerMatch ? parseInt(triggerMatch[2]) : 0,
    minute: triggerMatch ? parseInt(triggerMatch[3]) : 0,
    day_of_week: triggerMatch ? triggerMatch[1] : '*',
  }
  editDialog.value = true
}

const saveEdit = async () => {
  if (!editingSchedule.value) return

  try {
    const positionMm = editingSchedule.value.height * 10

    const scheduleData = {
      name: editingSchedule.value.name,
      action: editingSchedule.value.action,
      position_mm: positionMm,
      cron: {
        hour: editingSchedule.value.hour,
        minute: editingSchedule.value.minute,
        day_of_week: editingSchedule.value.day_of_week,
      },
      id: editingSchedule.value.id,
    }

    await schedulerService.createSchedule(scheduleData) // POST with same ID will replace
    scheduleFeedbackMessage.value = `Schedule "${editingSchedule.value.name}" updated successfully!`
    scheduleFeedbackType.value = 'success'
    scheduleFeedbackVisible.value = true

    editDialog.value = false
    editingSchedule.value = null
    await loadSchedules()

    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
  } catch (error: any) {
    console.error('Error updating schedule:', error)
    scheduleFeedbackMessage.value = error.response?.data?.detail || 'Failed to update schedule.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 5000)
  }
}

const formatNextRun = (nextRun: string | null) => {
  if (!nextRun) return 'Not scheduled'
  try {
    const date = new Date(nextRun)
    return date.toLocaleString('en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short',
    })
  } catch {
    return nextRun
  }
}

// Load schedules on mount
onMounted(() => {
  loadSchedules()
})
</script>

<template>
  <RequireRole :roles="['admin']">
    <v-container fluid class="pa-6">
      <!-- Header -->
      <v-row class="mb-6">
        <v-col cols="12">
          <h1 class="text-h4 font-weight-bold">Manage Desks</h1>
          <p class="text-body-1 text-medium-emphasis mt-2">
            Control desk heights immediately or schedule recurring adjustments.
          </p>
        </v-col>
      </v-row>

      <!-- Immediate Height Change -->
      <v-card elevation="2" class="pa-6 mb-6">
        <h2 class="text-h5 mb-4">Immediate Height Change</h2>
        <v-row align="center">
          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="deskHeight"
              label="Set Desk Height (cm)"
              type="number"
              min="68"
              max="120"
              hint="Valid range: 68-120 cm (680-1200 mm)"
              persistent-hint
              :disabled="isChangingHeight"
              variant="outlined"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-btn
              color="primary"
              size="large"
              @click="changeHeightForAllDesks"
              :loading="isChangingHeight"
              :disabled="isChangingHeight"
              block
            >
              <v-icon start>mdi-arrow-up-down</v-icon>
              Change Height (All Desks)
            </v-btn>
          </v-col>
        </v-row>

        <v-alert v-if="changeHeightFeedbackVisible" :type="changeHeightFeedbackType" class="mt-4">
          {{ changeHeightFeedbackMessage }}
        </v-alert>
      </v-card>

      <!-- Schedule Management Tabs -->
      <v-card elevation="2" class="pa-6">
        <v-tabs v-model="scheduleTab" color="primary" class="mb-4">
          <v-tab value="create">Create Schedule</v-tab>
          <v-tab value="manage">Manage Schedules ({{ schedules.length }})</v-tab>
        </v-tabs>

        <v-window v-model="scheduleTab">
          <!-- Create Schedule Tab -->
          <v-window-item value="create">
            <h2 class="text-h5 mb-4">Create New Schedule</h2>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="scheduleName"
                  label="Schedule Name *"
                  variant="outlined"
                  hint="e.g., Morning Standup, Cleaning Mode"
                  persistent-hint
                  :disabled="isCreatingSchedule"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="scheduleId"
                  label="Schedule ID (Optional)"
                  variant="outlined"
                  hint="Leave empty to auto-generate from name"
                  persistent-hint
                  :disabled="isCreatingSchedule"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="scheduleHeight"
                  label="Target Height (cm) *"
                  type="number"
                  min="68"
                  max="120"
                  variant="outlined"
                  hint="68-120 cm"
                  persistent-hint
                  :disabled="isCreatingSchedule"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="scheduleDayOfWeek"
                  :items="dayOfWeekOptions"
                  label="Days to Run *"
                  variant="outlined"
                  :disabled="isCreatingSchedule"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="scheduleHour"
                  label="Hour (0-23) *"
                  type="number"
                  min="0"
                  max="23"
                  variant="outlined"
                  hint="24-hour format"
                  persistent-hint
                  :disabled="isCreatingSchedule"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="scheduleMinute"
                  label="Minute (0-59) *"
                  type="number"
                  min="0"
                  max="59"
                  variant="outlined"
                  :disabled="isCreatingSchedule"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-btn
                  color="success"
                  size="large"
                  @click="createSchedule"
                  :loading="isCreatingSchedule"
                  :disabled="isCreatingSchedule"
                  block
                >
                  <v-icon start>mdi-calendar-plus</v-icon>
                  Create Schedule
                </v-btn>
              </v-col>
            </v-row>

            <v-alert v-if="scheduleFeedbackVisible" :type="scheduleFeedbackType" class="mt-4">
              {{ scheduleFeedbackMessage }}
            </v-alert>
          </v-window-item>

          <!-- Manage Schedules Tab -->
          <v-window-item value="manage">
            <div class="d-flex justify-space-between align-center mb-4">
              <h2 class="text-h5">Active Schedules</h2>
              <v-btn
                color="primary"
                variant="text"
                @click="loadSchedules"
                :loading="isLoadingSchedules"
                :disabled="isLoadingSchedules"
              >
                <v-icon start>mdi-refresh</v-icon>
                Refresh
              </v-btn>
            </div>

            <v-progress-linear
              v-if="isLoadingSchedules"
              indeterminate
              color="primary"
              class="mb-4"
            />

            <v-alert v-if="schedules.length === 0 && !isLoadingSchedules" type="info" class="mb-4">
              No schedules found. Create your first schedule in the "Create Schedule" tab.
            </v-alert>

            <v-row>
              <v-col v-for="schedule in schedules" :key="schedule.id" cols="12" md="6" lg="4">
                <v-card elevation="1" class="h-100">
                  <v-card-title class="d-flex align-center justify-space-between">
                    <span>{{ schedule.name }}</span>
                    <v-chip size="small" color="primary">{{ schedule.id }}</v-chip>
                  </v-card-title>

                  <v-card-text>
                    <div class="mb-2">
                      <v-icon size="small" class="mr-2">mdi-clock-outline</v-icon>
                      <strong>Next Run:</strong>
                      {{ formatNextRun(schedule.next_run) }}
                    </div>
                    <div class="mb-2">
                      <v-icon size="small" class="mr-2">mdi-calendar</v-icon>
                      <strong>Schedule:</strong>
                      {{ schedule.trigger }}
                    </div>
                  </v-card-text>

                  <v-card-actions>
                    <v-btn
                      color="info"
                      variant="text"
                      size="small"
                      @click="openEditDialog(schedule)"
                    >
                      <v-icon start>mdi-pencil</v-icon>
                      Edit
                    </v-btn>
                    <v-spacer />
                    <v-btn
                      color="error"
                      variant="text"
                      size="small"
                      @click="deleteSchedule(schedule.id, schedule.name)"
                    >
                      <v-icon start>mdi-delete</v-icon>
                      Delete
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>

            <v-alert v-if="scheduleFeedbackVisible" :type="scheduleFeedbackType" class="mt-4">
              {{ scheduleFeedbackMessage }}
            </v-alert>
          </v-window-item>
        </v-window>
      </v-card>

      <!-- Edit Schedule Dialog -->
      <v-dialog v-model="editDialog" max-width="600">
        <v-card v-if="editingSchedule">
          <v-card-title class="text-h5">Edit Schedule</v-card-title>

          <v-card-text>
            <v-alert type="info" variant="tonal" density="compact" class="mb-4">
              Editing schedule: <strong>{{ editingSchedule.id }}</strong>
            </v-alert>

            <v-text-field
              v-model="editingSchedule.name"
              label="Schedule Name"
              variant="outlined"
              class="mb-3"
            />

            <v-text-field
              v-model.number="editingSchedule.height"
              label="Target Height (cm)"
              type="number"
              min="68"
              max="120"
              variant="outlined"
              hint="68-120 cm"
              persistent-hint
              class="mb-3"
            />

            <v-select
              v-model="editingSchedule.day_of_week"
              :items="dayOfWeekOptions"
              label="Days to Run"
              variant="outlined"
              class="mb-3"
            />

            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model.number="editingSchedule.hour"
                  label="Hour (0-23)"
                  type="number"
                  min="0"
                  max="23"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model.number="editingSchedule.minute"
                  label="Minute (0-59)"
                  type="number"
                  min="0"
                  max="59"
                  variant="outlined"
                />
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn color="grey" variant="text" @click="editDialog = false"> Cancel </v-btn>
            <v-btn color="primary" variant="flat" @click="saveEdit">
              <v-icon start>mdi-content-save</v-icon>
              Save Changes
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </RequireRole>
</template>

<style scoped>
.h-100 {
  height: 100%;
}
</style>
