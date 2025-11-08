import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom'
import './index.css'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import QrGenerator from './pages/QrGenerator'
import QrList from './pages/QrList'
import Products from './pages/Products'
import Customers from './pages/Customers'
import Analytics from './pages/Analytics'
import ScanLog from './pages/ScanLog'
import Settings from './pages/Settings'
import Login from './pages/Login'

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="qrcodes/generate" element={<QrGenerator />} />
        <Route path="qrcodes" element={<QrList />} />
        <Route path="products" element={<Products />} />
        <Route path="customers" element={<Customers />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="scan-log" element={<ScanLog />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  </BrowserRouter>
)

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
