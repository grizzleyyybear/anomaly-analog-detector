'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export interface SignalPoint {
  value: number;
  time: string;
  timestamp: string;
}

export interface AnomalyEntry {
  status: string;
  timestamp: string;
  time: string;
  reconstructionError: number | null;
}

interface ChartDataPoint extends SignalPoint {
  anomaly: number | null;
}

export interface SignalChartProps {
  data: SignalPoint[];
  anomalyLog: AnomalyEntry[];
}

export default function SignalChart({ data, anomalyLog }: SignalChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="chart-placeholder">
        <p>Waiting for signal data...</p>
      </div>
    );
  }

  const chartData = data.map(point => ({
    ...point,
    anomaly: anomalyLog.some(a =>
      a.status === 'Anomaly Detected' &&
      Math.abs(new Date(a.timestamp).getTime() - new Date(point.timestamp).getTime()) < 2000
    ) ? point.value : null,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="time"
          stroke="#64748b"
          tick={{ fontSize: 11 }}
          interval="preserveStartEnd"
        />
        <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#e2e8f0',
          }}
        />
        <Line
          type="monotone"
          dataKey="value"
          stroke="#06b6d4"
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
        <Line
          type="monotone"
          dataKey="anomaly"
          stroke="#ef4444"
          strokeWidth={0}
          dot={{ fill: '#ef4444', r: 4 }}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
