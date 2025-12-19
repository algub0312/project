<script setup lang="ts">
defineProps<{
  icon: string
  color: string
  title: string
  subtitle: string
}>()
</script>

<template>
  <v-list-item>
    <template v-slot:prepend>
      <v-icon :color="color">{{ icon }}</v-icon>
    </template>
    <v-list-item-title>{{ title }}</v-list-item-title>
    <v-list-item-subtitle>{{ subtitle }}</v-list-item-subtitle>
  </v-list-item>
</template>
