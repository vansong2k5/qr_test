import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'

const Login = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@example.com')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      const res = await api.post('/auth/login', { email, password })
      localStorage.setItem('token', res.data.access_token)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Đăng nhập thất bại')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 dark:bg-slate-950">
      <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/60 p-6 shadow-lg space-y-4">
        <h1 className="text-xl font-semibold text-center">Đăng nhập</h1>
        <div>
          <label className="text-xs uppercase text-slate-500">Email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="text-xs uppercase text-slate-500">Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 w-full rounded-md border border-slate-300 bg-white/70 dark:bg-slate-900/40 px-3 py-2 text-sm" />
        </div>
        {error && <p className="text-sm text-rose-500">{error}</p>}
        <button type="submit" className="w-full rounded-md bg-indigo-500 px-4 py-2 text-white">Đăng nhập</button>
      </form>
    </div>
  )
}

export default Login
