import { useEffect, useState } from 'react'
import api from '../lib/api'
import { Product } from '../lib/types'

const Products = () => {
  const [items, setItems] = useState<Product[]>([])
  const [name, setName] = useState('')
  const [sku, setSku] = useState('')

  const load = () => api.get('/products').then((res) => setItems(res.data))

  useEffect(() => {
    load()
  }, [])

  const create = async () => {
    await api.post('/products', { name, sku })
    setName('')
    setSku('')
    load()
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-200 dark:border-slate-800 p-4">
        <h3 className="text-sm font-semibold mb-2">Thêm sản phẩm</h3>
        <div className="flex flex-wrap gap-2">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 px-3 py-2 text-sm" />
          <input value={sku} onChange={(e) => setSku(e.target.value)} placeholder="SKU" className="rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 px-3 py-2 text-sm" />
          <button onClick={create} className="rounded-md bg-indigo-500 px-3 py-2 text-white text-sm">Tạo</button>
        </div>
      </div>
      <ul className="space-y-2">
        {items.map((product) => (
          <li key={product.id} className="rounded-md border border-slate-200 dark:border-slate-800 px-4 py-3 flex justify-between">
            <span>
              <strong>{product.name}</strong> <span className="text-xs text-slate-500">({product.sku})</span>
            </span>
            <span className="text-xs text-slate-500">Owner: {product.owner_customer_id ?? '—'}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Products
