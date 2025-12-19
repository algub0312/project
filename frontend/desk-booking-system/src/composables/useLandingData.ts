import { ref } from 'vue'

export type Feature = { icon: string; color: string; title: string; description: string }
export type Step = { title: string; description: string }
export type Stat = { value: string; label: string }
export type Service = { name: string; value: number; status: 'Active' | 'Degraded' | 'Down' }

export function useLandingData() {
  const features = ref<Feature[]>([
    {
      icon: 'mdi-calendar-check',
      color: 'blue',
      title: 'Smart Booking',
      description: 'Reserve desks in advance or on-demand with real-time availability.',
    },
    {
      icon: 'mdi-radar',
      color: 'purple',
      title: 'Occupancy Detection',
      description: 'IoT sensors track desk usage automatically for accurate data.',
    },
    {
      icon: 'mdi-arrow-up-down',
      color: 'teal',
      title: 'Height Control',
      description: 'LINAK motorized desks with personalized settings.',
    },
  ])

  const steps = ref<Step[]>([
    {
      title: 'Browse Available Desks',
      description: 'View all desks with real-time availability and features.',
    },
    {
      title: 'Book Your Workspace',
      description: 'Select your desk and time slot with a few clicks.',
    },
    { title: 'Arrive & Work', description: 'Your desk is ready with personalized settings.' },
  ])

  const stats = ref<Stat[]>([
    { value: '100%', label: 'Office Utilization' },
    { value: '30%', label: 'Space Efficiency' },
    { value: '24/7', label: 'Availability' },
  ])

  const benefits = ref<Feature[]>([
    {
      title: 'Microservices Architecture',
      description: 'Scalable design with separate services for users, bookings, and occupancy.',
      icon: 'mdi-check',
      color: 'success',
    },
    {
      title: 'Real-time Monitoring',
      description: 'MQTT and RabbitMQ for instant updates and communication.',
      icon: 'mdi-check',
      color: 'success',
    },
    {
      title: 'Secure Authentication',
      description: 'Keycloak integration for enterprise-grade security.',
      icon: 'mdi-check',
      color: 'success',
    },
    {
      title: 'Containerized Deployment',
      description: 'Docker Compose for consistent environments.',
      icon: 'mdi-check',
      color: 'success',
    },
  ])

  const services = ref<Service[]>([
    { name: 'API Gateway', value: 100, status: 'Active' },
    { name: 'Booking Service', value: 100, status: 'Active' },
    { name: 'Occupancy Service', value: 100, status: 'Active' },
    { name: 'User Service', value: 100, status: 'Active' },
  ])

  return { features, steps, stats, benefits, services }
}
