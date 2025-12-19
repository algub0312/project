import { ref } from 'vue'

export const userViews = ref([
  { title: 'Book a Desk', to: '/book', icon: 'mdi-desk' },
  { title: 'My Bookings', to: '/my-bookings', icon: 'mdi-gavel' },
  { title: 'My Profile', to: '/profile', icon: 'mdi-account-box' },
])

export const adminViews = ref([
  { title: 'Manage Bookings', to: '/admin/bookings', icon: 'mdi-calendar-check' },
  { title: 'Manage Desks', to: '/admin/desks', icon: 'mdi-desk' },
  { title: 'Desk Availability', to: '/admin/availability', icon: 'mdi-calendar-multiple-check' },
  { title: 'Analytics', to: '/admin/analytics', icon: 'mdi-chart-bar' },
])
