<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { userViews, adminViews } from '@/composables/useViews'
import { useAuthStore } from '@/stores/auth.ts'
import { useRole } from '@/composables/auth/useRole.ts'
import { useSnackbarStore } from '@/stores/snackbar.ts'

const snackbar = useSnackbarStore()

const roles = useRole()

const router = useRouter()
const authStore = useAuthStore()

// Start with drawer open by default
const drawerVisibility = ref(true)

const closeDrawer = () => {
  drawerVisibility.value = false
}

const toggleDrawer = () => {
  drawerVisibility.value = !drawerVisibility.value
}

const theme = ref(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

const onLogin = async () => {
  await authStore.login()
}

const onLogout = async () => {
  await authStore.logout()
  closeDrawer()
  await router.push('/')
}
</script>

<template>
  <v-app :theme="theme">
    <v-navigation-drawer
      v-if="authStore.authenticated"
      v-model="drawerVisibility"
      color="primary"
      :permanent="drawerVisibility"
      width="280"
    >
      <v-list color="on-primary">
        <v-list-item
          v-for="item in roles.hasRole('admin') ? adminViews : userViews"
          :key="item.title"
          :title="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          link
        ></v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-4">
          <v-btn block @click="onLogout">Logout</v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar>
      <v-app-bar-nav-icon v-if="authStore.authenticated" @click="toggleDrawer"></v-app-bar-nav-icon>

      <v-app-bar-title>DeskHavn</v-app-bar-title>
      <v-btn
        :prepend-icon="theme === 'light' ? 'mdi-lightbulb-on-10' : 'mdi-lightbulb-on'"
        slim
        @click="toggleTheme"
      ></v-btn>
      <v-btn v-if="!authStore.authenticated" class="bg-primary" color="on-primary" @click="onLogin"
        >Login</v-btn
      >
    </v-app-bar>

    <v-main>
      <router-view v-slot="{ Component }">
        <v-fade-transition hide-on-leave>
          <component :is="Component" />
        </v-fade-transition>
      </router-view>
      <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="2500">
        {{ snackbar.message }}
      </v-snackbar>
    </v-main>
  </v-app>
</template>

<style scoped></style>
