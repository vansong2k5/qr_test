import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useOutletContext } from "react-router-dom";

import { createQRCode, fetchProducts, fetchQRCodes, revokeQRCode } from "../lib/api";
import type { LayoutContext } from "../components/Layout";
import type { Product, QrCode } from "../lib/types";

const reusableModes = [
  { value: "unlimited", label: "Tự do" },
  { value: "limited", label: "Giới hạn số lần" },
  { value: "phase", label: "Theo vòng đời sản phẩm" },
];

export const QRCodes = () => {
  const { user } = useOutletContext<LayoutContext>();
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [qrcodes, setQRCodes] = useState<QrCode[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [formLoading, setFormLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [form, setForm] = useState({
    productId: "",
    reusableMode: "unlimited",
    reuseLimit: "",
    payload: '{"redirect_url":"https://example.com"}',
    lifecyclePolicy: "",
    errorCorrection: "H",
    foreground: "#000000",
    background: "#FFFFFF",
    mask: null as File | null,
  });

  const productMap = useMemo(() => {
    const map = new Map<number, Product>();
    products.forEach((product) => map.set(product.id, product));
    return map;
  }, [products]);

  const loadProducts = useCallback(async () => {
    try {
      const data = await fetchProducts();
      setProducts(data);
      if (!form.productId && data.length > 0) {
        setForm((prev) => ({ ...prev, productId: data[0].id.toString() }));
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Không thể tải danh sách sản phẩm";
      setError(message);
    }
  }, [form.productId]);

  const loadQRCodes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const data = await fetchQRCodes(params);
      setQRCodes(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Không thể tải dữ liệu QR";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    void loadProducts();
  }, [loadProducts]);

  useEffect(() => {
    void loadQRCodes();
  }, [loadQRCodes]);

  const handleInputChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, files } = event.target as HTMLInputElement;
    if (name === "mask" && files) {
      setForm((prev) => ({ ...prev, mask: files[0] ?? null }));
      return;
    }
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (!form.productId) {
      setError("Vui lòng chọn sản phẩm cho QR");
      return;
    }

    try {
      if (form.payload) {
        JSON.parse(form.payload);
      }
      if (form.lifecyclePolicy) {
        JSON.parse(form.lifecyclePolicy);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "JSON không hợp lệ";
      setError(`Dữ liệu JSON không hợp lệ: ${message}`);
      return;
    }

    const formData = new FormData();
    formData.append("product_id", form.productId);
    formData.append("reusable_mode", form.reusableMode);
    formData.append("payload", form.payload || "{}");
    if (form.reuseLimit) {
      formData.append("reuse_limit", form.reuseLimit);
    }
    if (form.lifecyclePolicy) {
      formData.append("lifecycle_policy", form.lifecyclePolicy);
    }
    formData.append("error_correction", form.errorCorrection);
    formData.append("foreground", form.foreground);
    formData.append("background", form.background);
    if (form.mask) {
      formData.append("mask_image", form.mask);
    }

    setFormLoading(true);
    try {
      await createQRCode(formData);
      setSuccess("Tạo QR thành công");
      setForm((prev) => ({ ...prev, reuseLimit: "", mask: null }));
      await loadQRCodes();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Không thể tạo QR";
      setError(message);
    } finally {
      setFormLoading(false);
    }
  };

  const handleRevoke = async (qrcode: QrCode) => {
    setError(null);
    setSuccess(null);
    try {
      await revokeQRCode(qrcode.id);
      setSuccess(`Đã thu hồi QR ${qrcode.code}`);
      await loadQRCodes();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Không thể thu hồi QR";
      setError(message);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Quản lý mã QR</h1>
        <p className="text-gray-600">Theo dõi vòng đời QR do hệ thống phát hành và giám sát việc tái sử dụng.</p>
      </div>

      {error ? <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
      {success ? <div className="rounded border border-green-200 bg-green-50 p-3 text-sm text-green-700">{success}</div> : null}

      <div className="flex items-center gap-4">
        <label className="text-sm font-medium text-gray-700" htmlFor="status">
          Lọc theo trạng thái
        </label>
        <select
          id="status"
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
          className="rounded border px-3 py-2 text-sm"
        >
          <option value="">Tất cả</option>
          <option value="active">Đang hoạt động</option>
          <option value="inactive">Tạm dừng</option>
          <option value="revoked">Đã thu hồi</option>
        </select>
      </div>

      {user?.role === "admin" ? (
        <form onSubmit={handleCreate} className="rounded border border-gray-200 bg-white p-4 space-y-4 shadow-sm">
          <h2 className="text-lg font-semibold">Tạo QR mới</h2>
          {products.length === 0 ? (
            <div className="rounded border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-700">
              Cần có sản phẩm trước khi tạo QR. Hãy tạo sản phẩm mới trong mục Products.
            </div>
          ) : null}
          <div className="grid gap-4 md:grid-cols-2">
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Sản phẩm
              <select
                name="productId"
                value={form.productId}
                onChange={handleInputChange}
                className="mt-1 rounded border px-3 py-2"
                disabled={products.length === 0}
              >
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} ({product.sku})
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Chế độ sử dụng
              <select
                name="reusableMode"
                value={form.reusableMode}
                onChange={handleInputChange}
                className="mt-1 rounded border px-3 py-2"
              >
                {reusableModes.map((mode) => (
                  <option key={mode.value} value={mode.value}>
                    {mode.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Giới hạn tái sử dụng
              <input
                name="reuseLimit"
                type="number"
                value={form.reuseLimit}
                onChange={handleInputChange}
                min={0}
                className="mt-1 rounded border px-3 py-2"
                placeholder="Không giới hạn"
              />
            </label>
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Ảnh mask (tùy chọn)
              <input
                name="mask"
                type="file"
                accept="image/*"
                onChange={handleInputChange}
                className="mt-1"
              />
            </label>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Payload (JSON)
              <textarea
                name="payload"
                value={form.payload}
                onChange={handleInputChange}
                className="mt-1 rounded border px-3 py-2"
                rows={4}
              />
            </label>
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Chính sách vòng đời (JSON)
              <textarea
                name="lifecyclePolicy"
                value={form.lifecyclePolicy}
                onChange={handleInputChange}
                className="mt-1 rounded border px-3 py-2"
                rows={4}
                placeholder='{"allowed_statuses":["sold"]}'
              />
            </label>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Error correction
              <select
                name="errorCorrection"
                value={form.errorCorrection}
                onChange={handleInputChange}
                className="mt-1 rounded border px-3 py-2"
              >
                <option value="L">L</option>
                <option value="M">M</option>
                <option value="Q">Q</option>
                <option value="H">H</option>
              </select>
            </label>
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Màu nền
              <input
                name="background"
                type="color"
                value={form.background}
                onChange={handleInputChange}
                className="mt-1 h-10 w-full"
              />
            </label>
            <label className="flex flex-col text-sm font-medium text-gray-700">
              Màu QR
              <input
                name="foreground"
                type="color"
                value={form.foreground}
                onChange={handleInputChange}
                className="mt-1 h-10 w-full"
              />
            </label>
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
              disabled={formLoading || products.length === 0}
            >
              {formLoading ? "Đang tạo..." : "Tạo QR"}
            </button>
          </div>
        </form>
      ) : (
        <div className="rounded border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
          Chỉ quản trị viên mới được phép tạo hoặc thu hồi mã QR. Liên hệ bộ phận vận hành nếu bạn cần hỗ trợ.
        </div>
      )}

      <div className="rounded border border-gray-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">Mã QR</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">Sản phẩm</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">Chế độ</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">Trạng thái</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">Tái sử dụng</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">Vòng đời</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-600">Sự kiện</th>
                {user?.role === "admin" ? <th className="px-4 py-3 text-right font-semibold text-gray-600">Tác vụ</th> : null}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {loading ? (
                <tr>
                  <td colSpan={user?.role === "admin" ? 8 : 7} className="px-4 py-6 text-center text-gray-500">
                    Đang tải dữ liệu...
                  </td>
                </tr>
              ) : qrcodes.length === 0 ? (
                <tr>
                  <td colSpan={user?.role === "admin" ? 8 : 7} className="px-4 py-6 text-center text-gray-500">
                    Chưa có mã QR nào.
                  </td>
                </tr>
              ) : (
                qrcodes.map((qrcode) => (
                  <tr key={qrcode.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{qrcode.code}</td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-800">{productMap.get(qrcode.product_id)?.name ?? `Sản phẩm #${qrcode.product_id}`}</div>
                      <div className="text-xs text-gray-500">SKU: {productMap.get(qrcode.product_id)?.sku ?? "N/A"}</div>
                    </td>
                    <td className="px-4 py-3 capitalize text-gray-700">{qrcode.reusable_mode}</td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold uppercase text-slate-600">
                        {qrcode.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {qrcode.reuse_count}
                      {qrcode.reuse_limit ? ` / ${qrcode.reuse_limit}` : ""}
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-700">{qrcode.lifecycle_state}</div>
                      <div className="text-xs text-gray-500">
                        {qrcode.activated_at ? `Hoạt động: ${new Date(qrcode.activated_at).toLocaleString()}` : "Chưa kích hoạt"}
                      </div>
                      {qrcode.retired_at ? (
                        <div className="text-xs text-gray-500">Kết thúc: {new Date(qrcode.retired_at).toLocaleString()}</div>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      <details>
                        <summary className="cursor-pointer text-xs text-blue-600">
                          {qrcode.lifecycle_events.length} sự kiện
                        </summary>
                        <ul className="mt-2 space-y-1 text-xs text-gray-600">
                          {qrcode.lifecycle_events.map((event) => (
                            <li key={event.id} className="flex justify-between gap-4">
                              <span className="font-medium">{event.event_type}</span>
                              <span>{new Date(event.occurred_at).toLocaleString()}</span>
                            </li>
                          ))}
                        </ul>
                      </details>
                    </td>
                    {user?.role === "admin" ? (
                      <td className="px-4 py-3 text-right">
                        <button
                          type="button"
                          onClick={() => handleRevoke(qrcode)}
                          className="rounded bg-red-500 px-3 py-1 text-xs font-semibold text-white hover:bg-red-600 disabled:opacity-60"
                          disabled={qrcode.status === "revoked"}
                        >
                          Thu hồi
                        </button>
                      </td>
                    ) : null}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
