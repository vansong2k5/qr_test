import { FormEvent, useState } from 'react'
import api from '../lib/api'
import Card from '../components/Card'

const defaultOptions = {
  size: 400,
  ecc: 'H',
  fg_color: '#000000',
  bg_color: '#ffffff',
  margin: 4,
  logo_enabled: false,
}

const QrGenerator = () => {
  const [data, setData] = useState('{"url":"https://example.com"}')
  const [productId, setProductId] = useState('')
  const [customerId, setCustomerId] = useState('')
  const [reuseAllowed, setReuseAllowed] = useState(true)
  const [mask, setMask] = useState<File | null>(null)
  const [logo, setLogo] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>('')
  const [message, setMessage] = useState<string>('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const form = new FormData()
    form.append('data', data)
    if (productId) form.append('product_id', productId)
    if (customerId) form.append('customer_id', customerId)
    form.append('reuse_allowed', String(reuseAllowed))
    form.append('options', JSON.stringify(defaultOptions))
    if (mask) form.append('mask_image', mask)
    if (logo) form.append('logo_image', logo)
    try {
      const res = await api.post('/qrcodes/generate', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setPreview(res.data.image_url_png)
      setMessage('Tạo thành công!')
    } catch (error: any) {
      setMessage(error.response?.data?.detail ?? 'Lỗi tạo QR')
    }
  }

  const handleTestDecode = async () => {
    if (!preview) return
    const resp = await fetch(preview)
    const blob = await resp.blob()
    const form = new FormData()
    form.append('image', blob, 'qr.png')
    const res = await api.post('/qrcodes/test-decode', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    setMessage(res.data.decoded ? `Decode OK: ${res.data.decoded}` : 'Không decode được')
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">QR Generator</h2>
      <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
        <Card title="Thông tin nội dung">
          <label className="block text-xs uppercase text-slate-500">Data JSON/URL</label>
          <textarea
            value={data}
            onChange={(e) => setData(e.target.value)}
            className="w-full mt-2 rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 p-2"
            rows={6}
          />
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs uppercase text-slate-500">Product ID</label>
              <input value={productId} onChange={(e) => setProductId(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 p-2" />
            </div>
            <div>
              <label className="block text-xs uppercase text-slate-500">Customer ID</label>
              <input value={customerId} onChange={(e) => setCustomerId(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 p-2" />
            </div>
          </div>
          <label className="mt-4 flex items-center gap-2 text-sm">
            <input type="checkbox" checked={reuseAllowed} onChange={(e) => setReuseAllowed(e.target.checked)} /> Cho phép tái sử dụng
          </label>
        </Card>
        <Card title="Mask & Logo">
          <label className="block text-xs uppercase text-slate-500">Mask image (PNG/JPG)</label>
          <input type="file" accept="image/*" onChange={(e) => setMask(e.target.files?.[0] ?? null)} className="mt-2 text-sm" />
          <p className="text-xs mt-2 text-slate-500">Ảnh mask sẽ quyết định vùng đen của QR. Thuật toán tự giãn nếu mật độ không đủ.</p>
          <label className="block text-xs uppercase text-slate-500 mt-4">Logo trung tâm</label>
          <input type="file" accept="image/*" onChange={(e) => setLogo(e.target.files?.[0] ?? null)} className="mt-2 text-sm" />
          <p className="text-xs mt-2 text-slate-500">Khi chèn logo sẽ dùng ECC H để bảo vệ module quan trọng.</p>
        </Card>
        <div className="md:col-span-2 flex items-center gap-3">
          <button type="submit" className="rounded-md bg-indigo-500 px-4 py-2 text-white">Generate & Save</button>
          <button type="button" onClick={handleTestDecode} className="rounded-md bg-slate-200 dark:bg-slate-800 px-4 py-2">Test decode</button>
          {message && <span className="text-sm text-slate-500">{message}</span>}
        </div>
      </form>
      {preview && (
        <div className="md:flex items-start gap-6">
          <img src={preview} alt="QR preview" className="w-48 h-48 border border-slate-200 dark:border-slate-800 rounded-lg" />
          <p className="text-sm text-slate-500">Xem trước mã QR được render theo mask. Đảm bảo vùng finder (3 góc) luôn đen để dễ quét.</p>
        </div>
      )}
    </div>
  )
}

export default QrGenerator
