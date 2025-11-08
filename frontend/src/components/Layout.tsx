import { useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { MoonIcon, SunIcon } from '@heroicons/react/24/solid'

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/qrcodes/generate', label: 'QR Generator' },
  { to: '/qrcodes', label: 'QR List' },
  { to: '/products', label: 'Products' },
  { to: '/customers', label: 'Customers' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/scan-log', label: 'Scan Log' },
  { to: '/settings', label: 'Settings' },
]

const Layout = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [dark, setDark] = useState(true)

  const toggleTheme = () => {
    setDark((prev) => !prev)
    document.documentElement.classList.toggle('dark')
  }

  const logout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className={dark ? 'dark' : ''}>
      <div className="min-h-screen bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
        <header className="border-b border-slate-200 dark:border-slate-800">
          <div className="max-w-6xl mx-auto flex items-center justify-between py-4 px-6">
            <h1 className="text-xl font-semibold">QR Lifecycle Platform</h1>
            <div className="flex items-center gap-3">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-full bg-slate-200 dark:bg-slate-800"
                aria-label="Toggle dark mode"
              >
                {dark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
              </button>
              <button onClick={logout} className="text-sm text-rose-500">Đăng xuất</button>
            </div>
          </div>
        </header>
        <div className="max-w-6xl mx-auto px-6 py-6 grid md:grid-cols-[220px_1fr] gap-6">
          <nav className="space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={`block rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  location.pathname === item.to
                    ? 'bg-indigo-500 text-white'
                    : 'hover:bg-slate-200 dark:hover:bg-slate-800'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <main className="rounded-xl bg-white/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="p-6">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}

export default Layout
