const Settings = () => (
  <div className="space-y-4">
    <h2 className="text-2xl font-semibold">Cấu hình</h2>
    <p className="text-sm text-slate-500">
      Thiết lập .env, webhook và API key được quản lý ở backend. Sử dụng docker-compose để cập nhật biến môi trường
      như <code>JWT_SECRET</code>, <code>RATE_LIMIT_SCAN_PER_MINUTE</code>.
    </p>
    <p className="text-sm text-slate-500">
      Để nhận webhook khi quét, tạo bản ghi mới qua API <code>/api/webhooks</code> (chưa có UI). Tích hợp Redis phục vụ rate-limit.
    </p>
  </div>
)

export default Settings
