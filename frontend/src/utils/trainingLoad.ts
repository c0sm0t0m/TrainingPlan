export interface LoadPoint {
  date: string
  tss: number
  ctl: number
  atl: number
  tsb: number
}

export interface LoadSummary {
  ctl: number
  atl: number
  tsb: number
  weekly_tss: number
  trend: 'up' | 'down' | 'flat'
}

/** Same weekly TSS and trend rules as the backend training-metrics endpoint. */
export function summarizeLoad(metrics: LoadPoint[]): LoadSummary {
  if (metrics.length === 0) {
    return { ctl: 0, atl: 0, tsb: 0, weekly_tss: 0, trend: 'flat' }
  }

  const current = metrics[metrics.length - 1]
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const monday = new Date(today)
  const weekday = (today.getDay() + 6) % 7
  monday.setDate(today.getDate() - weekday)

  let weeklyTss = 0
  for (const day of metrics) {
    const dayDate = new Date(`${day.date}T00:00:00`)
    if (dayDate >= monday && dayDate <= today) {
      weeklyTss += day.tss || 0
    }
  }

  let trend: LoadSummary['trend'] = 'flat'
  if (metrics.length >= 8) {
    const previousCtl = metrics[metrics.length - 8].ctl
    if (current.ctl > previousCtl) trend = 'up'
    else if (current.ctl < previousCtl) trend = 'down'
  }

  return {
    ctl: current.ctl,
    atl: current.atl,
    tsb: current.tsb,
    weekly_tss: Math.round(weeklyTss * 10) / 10,
    trend,
  }
}
