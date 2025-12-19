// HH:mm → hours number
export function hoursBetween(startTime: string, endTime: string): number {
  const [sh, sm] = startTime.split(':').map(Number)
  const [eh, em] = endTime.split(':').map(Number)
  return (eh * 60 + em - (sh * 60 + sm)) / 60
}

// Monday-based week (locale DK)
export function getWeekBounds(d = new Date()): { start: Date; end: Date } {
  const date = new Date(d)
  const day = (date.getDay() + 6) % 7 // 0 = Monday
  const start = new Date(date)
  start.setDate(date.getDate() - day)
  start.setHours(0, 0, 0, 0)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  end.setHours(23, 59, 59, 999)
  return { start, end }
}

export function todayISO(): string {
  return new Date().toISOString().split('T')[0]
}

export function getWeekDays(): { dayName: string; date: string; isToday: boolean }[] {
  const { start } = getWeekBounds(new Date())
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    days.push({
      dayName: d.toLocaleDateString('en-GB', { weekday: 'short' }), // Mon..Sun
      date: d.toISOString().split('T')[0],
      isToday: d.toDateString() === new Date().toDateString(),
    })
  }
  return days
}
