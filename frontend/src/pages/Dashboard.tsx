import { useEffect, useState } from 'react'
import Card from '../components/Card'
import api from '../lib/api'

interface Summary {
  total_scans: number
  scans_today: number
  active_qr: number
  reuse_cycles: number
}

const Dashboard = () => {
  const [summary, setSummary] = useState<Summary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/analytics/summary')
      .then((res) => setSummary(res.data.summary))
      .catch(() => setSummary(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <p>Đang tải...</p>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Tổng quan</h2>
      {summary ? (
        <div className="grid md:grid-cols-2 gap-4">
          <Card title="Tổng lượt quét">{summary.total_scans}</Card>
          <Card title="Quét hôm nay">{summary.scans_today}</Card>
          <Card title="QR đang hoạt động">{summary.active_qr}</Card>
          <Card title="Chu kỳ tái sử dụng">{summary.reuse_cycles}</Card>
        </div>
      ) : (
        <p>Chưa có dữ liệu. Hãy tạo QR đầu tiên!</p>
      )}
    </div>
  )
}

export default Dashboard
