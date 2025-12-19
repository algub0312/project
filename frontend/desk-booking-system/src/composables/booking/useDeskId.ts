import type { Desk } from '@/types/desk.ts'

export const fromDeskIdToDesk = (deskId: number, desks: Desk[]): Desk | undefined => {
  return desks.find((desk: Desk) => desk.id === deskId)
}
