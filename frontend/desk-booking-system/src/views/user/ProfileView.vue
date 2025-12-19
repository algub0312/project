<script setup lang="ts">
import DeskHeightCalculator from '@/components/DeskHeightCalculator.vue'
import RequireRole from '@/components/RequireRole.vue'
import { useAuthStore } from '@/stores/auth'
import { computed, onMounted, ref } from 'vue'
import { userService } from '@/services/api/userService.ts'
import type { DeskPreferences } from '@/types/deskPreferences.ts'

const auth = useAuthStore()
const user = computed(() => auth.user)

const userProfile = ref<{
  userHeightCm?: number
  preferredSittingHeightCm?: number
  preferredStandingHeightCm?: number
} | null>()

const isLoadingProfile = ref(false)

onMounted(async () => {
  if (!user.value?.id) return

  isLoadingProfile.value = true
  try {
    userProfile.value = await userService.getUserById(user.value.id)
  } catch (error) {
    console.error('Error fetching user profile:', error)
  } finally {
    isLoadingProfile.value = false
  }
})

const updateUserPreferences = async (data: {
  userHeight: number
  sittingHeight: number
  standingHeight: number
}) => {
  if (!user.value?.id) return

  try {
    await userService.updateDeskPreferences(user.value.id, data.userHeight, {
      sittingHeight: data.sittingHeight,
      standingHeight: data.standingHeight,
    } as DeskPreferences)

    userProfile.value = {
      userHeightCm: data.userHeight,
      preferredSittingHeightCm: data.sittingHeight,
      preferredStandingHeightCm: data.standingHeight,
    }
    console.log('Desk preferences saved successfully!')
  } catch (error) {
    console.error('Error saving desk preferences:', error)
  }
}
</script>

<template>
  <RequireRole :roles="['user']">
    <v-container class="pa-6 fill-height d-flex flex-column justify-center">
      <v-row align="center" class="flex-grow-1">
        <v-col cols="12" md="12" lg="6" class="d-flex flex-column align-center pa-8">
          <!-- Profile Header -->
          <v-card class="mb-6" elevation="2" min-width="500">
            <v-card-text class="text-center pa-8">
              <!-- Profile Picture -->
              <v-avatar size="120" class="mb-4" color="primary">
                <v-icon v-if="!user" size="60" color="white">mdi-account</v-icon>
              </v-avatar>

              <!-- User Information -->
              <div class="mb-6">
                <div class="mb-4">
                  <v-chip color="primary" variant="outlined" class="mb-2">Username</v-chip>
                  <div class="text-h6">{{ user?.username }}</div>
                </div>

                <div class="mb-4">
                  <v-chip color="primary" variant="outlined" class="mb-2">Full Name</v-chip>
                  <div class="text-h6">{{ user?.fullName }}</div>
                </div>

                <div class="mb-4">
                  <v-chip color="primary" variant="outlined" class="mb-2">Email</v-chip>
                  <div class="text-h6">{{ user?.email }}</div>
                </div>
              </div>
            </v-card-text>
            <v-row justify="center" class="mb-6">
              <v-btn size="large" rounded="lg" color="primary" @click="auth.editAccount()">
                Edit Profile
              </v-btn>
            </v-row>
          </v-card>
        </v-col>
        <v-col cols="12" md="12" lg="6" class="d-flex flex-column align-center pa-8">
          <v-progress-circular v-if="isLoadingProfile" indeterminate color="primary" />
          <DeskHeightCalculator
            v-else
            :initial-height="userProfile?.userHeightCm"
            :initial-sitting-height="userProfile?.preferredSittingHeightCm"
            :initial-standing-height="userProfile?.preferredStandingHeightCm"
            @save="updateUserPreferences"
          />
        </v-col>
      </v-row>
    </v-container>
  </RequireRole>
</template>
