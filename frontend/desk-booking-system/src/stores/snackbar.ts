// stores/snackbar.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSnackbarStore = defineStore('snackbar', () => {
  const show = ref(false)
  const message = ref('')
  const color = ref('')

  const open = (msg: string, clr = 'info') => {
    message.value = msg
    color.value = clr
    show.value = true
  }

  return {
    show,
    message,
    color,
    open,

    // helpers
    error: (msg: string) => open(msg, 'error'),
    success: (msg: string) => open(msg, 'success'),
    warning: (msg: string) => open(msg, 'warning'),
    info: (msg: string) => open(msg, 'info'),
  }
})
