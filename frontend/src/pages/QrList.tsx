import { useEffect, useState } from 'react'
import api from '../lib/api'
import { QrCode } from '../lib/types'

const QrList = () => {
  const [items, setItems] = useState<QrCode[]>([])
  const [query, setQuery] = useState('')

  const load = () => {
    api.get('/qrcodes', { params: { query } }).then((res) => setItems(res.data))
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <input
          className="rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 px-3 py-2 text-sm"
          placeholder="Tìm theo mã"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={load} className="rounded-md bg-indigo-500 px-4 py-2 text-white text-sm">Lọc</button>
      </div>
      <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-800">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800 text-sm">
          <thead className="bg-slate-100 dark:bg-slate-900">
            <tr>
              <th className="px-4 py-2 text-left">QR</th>
              <th className="px-4 py-2 text-left">Code ID</th>
              <th className="px-4 py-2 text-left">Product</th>
              <th className="px-4 py-2">Reuse</th>
              <th className="px-4 py-2">Active</th>
              <th className="px-4 py-2">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
            {items.map((qr) => (
              <tr key={qr.code_id}>
                <td className="px-4 py-2">
                  <img src={qr.image_url_png} alt="QR thumb" className="h-16 w-16 rounded border border-slate-200 dark:border-slate-700" />
                </td>
                <td className="px-4 py-2 font-mono text-xs">{qr.code_id}</td>
                <td className="px-4 py-2">{qr.product_id ?? '—'}</td>
                <td className="px-4 py-2 text-center">{qr.reuse_cycle}</td>
                <td className="px-4 py-2 text-center">{qr.active ? '✅' : '⛔️'}</td>
                <td className="px-4 py-2 text-xs text-slate-500">{new Date(qr.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default QrList
