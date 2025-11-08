import { useEffect, useState } from 'react'
import api from '../lib/api'

interface DailyCount {
  day: string
  count: number
}

const Analytics = () => {
  const [daily, setDaily] = useState<DailyCount[]>([])

  useEffect(() => {
    api.get('/analytics/summary').then((res) => setDaily(res.data.scans_by_day))
  }, [])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Biểu đồ lượt quét 30 ngày</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="px-4 py-2">Ngày</th>
              <th className="px-4 py-2">Lượt quét</th>
            </tr>
          </thead>
          <tbody>
            {daily.map((row) => (
              <tr key={row.day} className="border-t border-slate-200 dark:border-slate-800">
                <td className="px-4 py-2">{new Date(row.day).toLocaleDateString()}</td>
                <td className="px-4 py-2">
                  <div className="bg-indigo-500/30 h-3 rounded" style={{ width: `${row.count * 10}px` }} />
                  <span className="ml-2 text-xs">{row.count}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Analytics
