import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import type { App } from 'vue'

export function installTanStackQuery(app: App) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60, // 1 min
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  })

  app.use(VueQueryPlugin, { queryClient })
}
