import { Card, CardContent, Typography, Box } from '@mui/material'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface PerformanceChartProps {
  data: Array<{
    date: string
    ctl: number
    atl: number
    tsb: number
  }>
}

export default function PerformanceChart({ data }: PerformanceChartProps) {
  // Interpret TSB (Training Stress Balance)
  const currentTSB = data.length > 0 ? data[data.length - 1].tsb : 0
  
  // Debug: Log data range
  if (data.length > 0) {
    const firstDate = new Date(data[0].date);
    const lastDate = new Date(data[data.length - 1].date);
    console.log(`Performance Chart: ${data.length} days from ${firstDate.toLocaleDateString()} to ${lastDate.toLocaleDateString()}`);
  } else {
    console.log('Performance Chart: No data available');
  }
  
  let tsbInterpretation = ''
  let tsbColor = '#757575'
  
  if (currentTSB < -30) {
    tsbInterpretation = 'High Fatigue - Recovery needed'
    tsbColor = '#f44336'
  } else if (currentTSB < -10) {
    tsbInterpretation = 'Overreaching - Building fitness'
    tsbColor = '#ff9800'
  } else if (currentTSB < 5) {
    tsbInterpretation = 'Neutral - Maintaining fitness'
    tsbColor = '#2196f3'
  } else if (currentTSB < 20) {
    tsbInterpretation = 'Fresh - Ready to race'
    tsbColor = '#4caf50'
  } else {
    tsbInterpretation = 'Very Fresh - Detraining risk'
    tsbColor = '#9e9e9e'
  }

  return (
    <>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(date) => {
              const d = new Date(date)
              return `${d.getMonth() + 1}/${d.getDate()}`
            }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            labelFormatter={(date) => new Date(date).toLocaleDateString()}
            formatter={(value: number | undefined) => value ? value.toFixed(1) : '0'}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="ctl"
            name="Fitness (CTL)"
            stroke="#2196f3"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="atl"
            name="Fatigue (ATL)"
            stroke="#ff9800"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="tsb"
            name="Form (TSB)"
            stroke="#4caf50"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </>
  )
}
