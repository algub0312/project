import type { Booking } from '@/types/booking.ts'
import type { Desk } from '@/types/desk.ts'

export interface DeskDrawingData {
  deskId: number
  color: 'green' | 'red' | 'orange'
  positionX: number
  positionY: number
  orientation: 'horizontal' | 'vertical'
}

export function toDeskDrawingData(desks: Desk[], bookings: Booking[]) {
  return desks.map((desk) => {
    const booking = bookings.find((b) => b.deskId === desk.id)
    let color: 'green' | 'red' | 'orange' = 'green'
    if (desk.status === 'reserved' || booking) {
      color = 'orange'
    }
    return {
      deskId: desk.id,
      color,
      positionX: desk.positionX,
      positionY: desk.positionY,
      orientation: desk.orientation,
    }
  })
}
