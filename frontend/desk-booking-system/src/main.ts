import { createApp } from 'vue'
import { createPinia } from 'pinia'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'
import 'unfonts.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { initKeycloak } from '@/services/api/keycloak.ts'
import { handleLoginRedirect } from '@/composables/auth/useLoginRedirect.ts'

import { installTanStackQuery } from '@/plugins/tanStackQuery.ts'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
})

app.use(vuetify)

initKeycloak().then(async () => {
  const auth = useAuthStore()
  auth.init()
  if (window.location.pathname === '/' && auth.authenticated) {
    await handleLoginRedirect()
  }
  app.use(router)
  installTanStackQuery(app)
  app.mount('#app')
})
