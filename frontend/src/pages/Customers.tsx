import { useEffect, useState } from 'react'
import api from '../lib/api'
import { Customer } from '../lib/types'

const Customers = () => {
  const [items, setItems] = useState<Customer[]>([])
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')

  const load = () => api.get('/customers').then((res) => setItems(res.data))

  useEffect(() => {
    load()
  }, [])

  const create = async () => {
    await api.post('/customers', { name, email })
    setName('')
    setEmail('')
    load()
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-4">
        <h3 className="text-sm font-semibold mb-2">Thêm khách hàng</h3>
        <div className="flex flex-wrap gap-2">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 px-3 py-2 text-sm" />
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 px-3 py-2 text-sm" />
          <button onClick={create} className="rounded-md bg-indigo-500 px-3 py-2 text-white text-sm">Tạo</button>
        </div>
      </div>
      <ul className="space-y-2">
        {items.map((customer) => (
          <li key={customer.id} className="rounded-md border border-slate-200 dark:border-slate-800 px-4 py-3">
            <strong>{customer.name}</strong>
            <p className="text-xs text-slate-500">{customer.email ?? '—'}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Customers
