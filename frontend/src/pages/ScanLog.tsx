import { useEffect, useState } from 'react'
import api from '../lib/api'
import { ScanEvent } from '../lib/types'

const ScanLog = () => {
  const [events, setEvents] = useState<ScanEvent[]>([])

  useEffect(() => {
    api.get('/scans').then((res) => setEvents(res.data))
  }, [])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Lịch sử quét</h2>
      <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-800">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-100 dark:bg-slate-900">
            <tr>
              <th className="px-4 py-2 text-left">Thời gian</th>
              <th className="px-4 py-2 text-left">Device</th>
              <th className="px-4 py-2 text-left">Geo</th>
            </tr>
          </thead>
          <tbody>
            {events.map((ev) => (
              <tr key={ev.id} className="border-t border-slate-200 dark:border-slate-800">
                <td className="px-4 py-2">{new Date(ev.ts).toLocaleString()}</td>
                <td className="px-4 py-2">{ev.device ?? 'unknown'}</td>
                <td className="px-4 py-2 text-slate-500">{ev.approx_geo ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ScanLog
