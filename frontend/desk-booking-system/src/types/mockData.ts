// ========================================
// TYPES & INTERFACES
// ========================================

import type { Desk } from '@/types/desk.ts'
import type { DeskStatus } from '@/types/deskStatus.ts'
export type BookingStatus = 'active' | 'completed' | 'cancelled'

export interface DeskFeatures {
  nearWindow: boolean
  dualMonitor: boolean
  standingDesk?: boolean
}

export interface Booking {
  id: string
  deskId: number
  date: string // YYYY-MM-DD
  startTime: string // HH:mm
  endTime: string // HH:mm
  userId: string
  status: BookingStatus
  notes?: string
  createdAt: string // ISO date
}

export interface User {
  id: string
  username: string
  fullName: string
  email: string
  role: 'user' | 'admin'
  createdAt: string
  profilePicture?: string
}

// ========================================
// MOCK DATA
// ========================================
export const mockUsers: User[] = [
  {
    id: 'user-1',
    username: 'ana.popescu',
    fullName: 'Ana Popescu',
    email: 'ana.popescu@company.com',
    role: 'user',
    createdAt: '2024-01-15T08:00:00Z',
    profilePicture: 'https://i.pravatar.cc/150?img=1',
  },
  {
    id: 'user-2',
    username: 'ion.ionescu',
    fullName: 'Ion Ionescu',
    email: 'ion.ionescu@company.com',
    role: 'user',
    createdAt: '2024-01-20T09:30:00Z',
    profilePicture: 'https://i.pravatar.cc/150?img=2',
  },
  {
    id: 'user-3',
    username: 'maria.georgescu',
    fullName: 'Maria Georgescu',
    email: 'maria.georgescu@company.com',
    role: 'admin',
    createdAt: '2024-02-01T10:00:00Z',
    profilePicture: 'https://i.pravatar.cc/150?img=3',
  },
  {
    id: 'current-user',
    username: 'andrei.dumitrescu',
    fullName: 'Andrei Dumitrescu',
    email: 'andrei.dumitrescu@company.com',
    role: 'user',
    createdAt: '2024-02-10T11:15:00Z',
    profilePicture: 'https://i.pravatar.cc/150?img=4',
  },
]

export const mockDesks: Desk[] = [
  // FLOOR 0, COLUMN 1
  {
    id: 226478362196966,
    status: 'available',
    features: ['near-window'],
    floor: 0,
    isFavorite: false,
    positionX: 100,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 262106213020445,
    status: 'occupied',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 100,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 123827495865496,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 100,
    positionY: 330,
    orientation: 'vertical',
  },
  {
    id: 1017560220360,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 185,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 265329166565154,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 185,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 94703884467377,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 185,
    positionY: 330,
    orientation: 'vertical',
  },
  // FLOOR 0, COLUMN 2
  {
    id: 226742701698845,
    status: 'available',
    features: ['dual-monitor'],
    floor: 0,
    isFavorite: true,
    positionX: 500,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 159530725667917,
    status: 'occupied',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 500,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 243319249771104,
    status: 'available',
    features: ['near-window'],
    floor: 0,
    isFavorite: false,
    positionX: 500,
    positionY: 330,
    orientation: 'vertical',
  },
  {
    id: 248426105766080,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 585,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 19017354320526,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 585,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 17812868571456,
    status: 'occupied',
    features: ['near-window'],
    floor: 0,
    isFavorite: false,
    positionX: 585,
    positionY: 330,
    orientation: 'vertical',
  },
  // FLOOR 0, COLUMN 3
  {
    id: 27757512190365,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 900,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 31358723358021,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 900,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 42111826491855,
    status: 'occupied',
    features: ['dual-monitor'],
    floor: 0,
    isFavorite: true,
    positionX: 900,
    positionY: 330,
    orientation: 'vertical',
  },
  {
    id: 9991163689910,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 985,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 18529719313264,
    status: 'available',
    features: ['near-window'],
    floor: 0,
    isFavorite: false,
    positionX: 985,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 225668450932504,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 985,
    positionY: 330,
    orientation: 'vertical',
  },
  // FLOOR 0, BOTTOM ROW
  {
    id: 252847857963200,
    status: 'available',
    features: ['standing-desk'],
    floor: 0,
    isFavorite: false,
    positionX: 50,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 269563075450181,
    status: 'occupied',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 205,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 252109451510178,
    status: 'available',
    features: ['near-window', 'dual-monitor'],
    floor: 0,
    isFavorite: true,
    positionX: 360,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 127573335781430,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 515,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 272257688561719,
    status: 'occupied',
    features: ['standing-desk'],
    floor: 0,
    isFavorite: false,
    positionX: 670,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 141786854161105,
    status: 'available',
    features: [],
    floor: 0,
    isFavorite: false,
    positionX: 825,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 262261183250050,
    status: 'available',
    features: ['dual-monitor'],
    floor: 0,
    isFavorite: false,
    positionX: 980,
    positionY: 650,
    orientation: 'horizontal',
  },

  // FLOOR 1, COLUMN 1
  {
    id: 152576854556238,
    status: 'occupied',
    features: ['near-window'],
    floor: 1,
    isFavorite: false,
    positionX: 100,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 253275471407465,
    status: 'occupied',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 100,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 248358066594897,
    status: 'occupied',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 100,
    positionY: 330,
    orientation: 'vertical',
  },
  {
    id: 185995715787155,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 185,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 238886721026865,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 185,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 186401026010811,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 185,
    positionY: 330,
    orientation: 'vertical',
  },
  // FLOOR 1, COLUMN 2
  {
    id: 159004380108457,
    status: 'available',
    features: ['dual-monitor'],
    floor: 1,
    isFavorite: true,
    positionX: 500,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 78055838050678,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 500,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 271729642387908,
    status: 'available',
    features: ['near-window'],
    floor: 1,
    isFavorite: false,
    positionX: 500,
    positionY: 330,
    orientation: 'vertical',
  },
  {
    id: 216635771040543,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 585,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 5419435058722,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 585,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 49139000955870,
    status: 'available',
    features: ['near-window'],
    floor: 1,
    isFavorite: false,
    positionX: 585,
    positionY: 330,
    orientation: 'vertical',
  },
  // FLOOR 1, COLUMN 3
  {
    id: 24104978543313,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 900,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 26222032310050,
    status: 'occupied',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 900,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 165962038374518,
    status: 'available',
    features: ['dual-monitor'],
    floor: 1,
    isFavorite: true,
    positionX: 900,
    positionY: 330,
    orientation: 'vertical',
  },
  {
    id: 214371580088177,
    status: 'occupied',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 985,
    positionY: 20,
    orientation: 'vertical',
  },
  {
    id: 207776391483948,
    status: 'available',
    features: ['near-window'],
    floor: 1,
    isFavorite: false,
    positionX: 985,
    positionY: 175,
    orientation: 'vertical',
  },
  {
    id: 27510629123607,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 985,
    positionY: 330,
    orientation: 'vertical',
  },
  // FLOOR 1, BOTTOM ROW
  {
    id: 62633840006583,
    status: 'occupied',
    features: ['standing-desk'],
    floor: 1,
    isFavorite: false,
    positionX: 50,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 106859788739998,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 205,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 38456082749717,
    status: 'available',
    features: ['near-window', 'dual-monitor'],
    floor: 1,
    isFavorite: true,
    positionX: 360,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 236480784423714,
    status: 'available',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 515,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 227517560538229,
    status: 'occupied',
    features: ['standing-desk'],
    floor: 1,
    isFavorite: false,
    positionX: 670,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 129080909134627,
    status: 'occupied',
    features: [],
    floor: 1,
    isFavorite: false,
    positionX: 825,
    positionY: 650,
    orientation: 'horizontal',
  },
  {
    id: 178123056043286,
    status: 'occupied',
    features: ['dual-monitor'],
    floor: 1,
    isFavorite: false,
    positionX: 980,
    positionY: 650,
    orientation: 'horizontal',
  },
]

export const mockBookings: Booking[] = [
  {
    id: 'booking-1',
    deskId: 226478362196966,
    date: '2025-10-05',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'current-user',
    status: 'active',
    createdAt: '2025-10-03T14:30:00Z',
  },
  {
    id: 'booking-2',
    deskId: 123827495865496,
    date: '2025-09-29',
    startTime: '09:00',
    endTime: '13:00',
    userId: 'current-user',
    status: 'active',
    notes: 'Half day work',
    createdAt: '2025-09-28T10:15:00Z',
  },
  {
    id: 'booking-3',
    deskId: 123827495865496,
    date: '2025-09-26',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'current-user',
    status: 'completed',
    createdAt: '2025-09-25T16:45:00Z',
  },
  {
    id: 'booking-4',
    deskId: 123827495865496,
    date: '2025-09-25',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'current-user',
    status: 'completed',
    createdAt: '2025-09-24T08:00:00Z',
  },
]

// ========================================
// HELPER FUNCTIONS
// ========================================

export const mockDataHelpers = {
  // Desk helpers
  desks: {
    getAll: () => mockDesks,
    getById: (id: number) => mockDesks.find((desk) => desk.id === id),
    getAvailable: () => mockDesks.filter((desk) => desk.status === 'available'),
    getOccupied: () => mockDesks.filter((desk) => desk.status === 'occupied'),
    getByStatus: (status: DeskStatus) => mockDesks.filter((desk) => desk.status === status),
    getByFloor: (floor: number) => mockDesks.filter((desk) => desk.floor === floor),
    getOccupiedByFloor: (floor: number) =>
      mockDesks.filter((desk) => desk.floor === floor && desk.status === 'occupied'),
    getFavorites: () => mockDesks.filter((desk) => desk.isFavorite),
    getByFeature: (feature: string) => mockDesks.filter((desk) => desk.features.includes(feature)),
    getByUser: (userId: string) => mockDesks.filter((desk) => desk.bookedBy === userId),
  },

  // Booking helpers
  bookings: {
    getAll: () => mockBookings,
    getById: (id: string) => mockBookings.find((booking) => booking.id === id),
    getByUserId: (userId: string) => mockBookings.filter((booking) => booking.userId === userId),
    getByDeskId: (deskId: number) => mockBookings.filter((booking) => booking.deskId === deskId),
    getByDate: (date: string) => mockBookings.filter((booking) => booking.date === date),
    getByHour: (time: string) => mockBookings.filter((booking) => booking.startTime === time),
    getActive: () => mockBookings.filter((booking) => booking.status === 'active'),
    getCompleted: () => mockBookings.filter((booking) => booking.status === 'completed'),
    getCancelled: () => mockBookings.filter((booking) => booking.status === 'cancelled'),
    getByStatus: (status: BookingStatus) =>
      mockBookings.filter((booking) => booking.status === status),
  },

  // User helpers
  users: {
    getAll: () => mockUsers,
    getById: (id: string) => mockUsers.find((user) => user.id === id),
    getByEmail: (email: string) => mockUsers.find((user) => user.email === email),
    getByRole: (role: 'user' | 'admin') => mockUsers.filter((user) => user.role === role),
    getCurrentUser: () => mockUsers.find((user) => user.id === 'current-user'),
  },
}
export const deskOccupancy = [
  { title: 'Used Desks', value: mockDataHelpers.desks.getOccupied().length },
  { title: 'Unused Desks', value: mockDataHelpers.desks.getAvailable().length },
]

export const plByTime = [
  { title: '07:00', value: mockDataHelpers.bookings.getByHour('07:00').length },
  { title: '08:00', value: mockDataHelpers.bookings.getByHour('08:00').length },
  { title: '09:00', value: mockDataHelpers.bookings.getByHour('09:00').length },
  { title: '10:00', value: mockDataHelpers.bookings.getByHour('10:00').length },
  { title: '11:00', value: mockDataHelpers.bookings.getByHour('11:00').length },
  { title: '12:00', value: mockDataHelpers.bookings.getByHour('12:00').length },
  { title: '13:00', value: mockDataHelpers.bookings.getByHour('13:00').length },
  { title: '14:00', value: mockDataHelpers.bookings.getByHour('14:00').length },
  { title: '15:00', value: mockDataHelpers.bookings.getByHour('15:00').length },
  { title: '16:00', value: mockDataHelpers.bookings.getByHour('16:00').length },
  { title: '17:00', value: mockDataHelpers.bookings.getByHour('17:00').length },
  { title: '18:00', value: mockDataHelpers.bookings.getByHour('18:00').length },
]

export const plByFloor = [
  { title: '1st Floor', value: mockDataHelpers.desks.getOccupiedByFloor(0).length },
  { title: '2nd Floor', value: mockDataHelpers.desks.getOccupiedByFloor(1).length },
]

// Export
export const mockData = {
  desks: mockDesks,
  bookings: mockBookings,
  users: mockUsers,
  helpers: mockDataHelpers,
}
