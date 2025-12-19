import type { DeskStatus } from '@/types/deskStatus.ts'

export interface Desk {
  id: number
  status: DeskStatus
  features: string[]
  floor: number
  bookedBy?: string
  isFavorite?: boolean
  height?: number
  positionX: number
  positionY: number
  orientation: 'horizontal' | 'vertical'
}
