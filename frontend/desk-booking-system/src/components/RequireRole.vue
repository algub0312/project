<script setup lang="ts">
import { useRole } from '@/composables/auth/useRole.ts'
import router from '@/router'
import { onMounted } from 'vue'

const props = defineProps<{
  roles: string[] // required roles
}>()

const { hasAnyRole } = useRole()

onMounted(() => {
  if (!hasAnyRole(...props.roles)) {
    router.replace('/unauthorized')
  }
})
</script>

<template>
  <div>
    <slot />
  </div>
</template>

<style scoped></style>
