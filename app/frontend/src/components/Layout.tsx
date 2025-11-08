import { useCallback, useEffect, useState } from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";

import { fetchCurrentUser } from "../lib/api";
import type { User } from "../lib/types";

export type LayoutContext = {
  user: User | null;
  refreshUser: () => Promise<void>;
};

export default function Layout() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setUser(null);
      setLoading(false);
      navigate("/login", { replace: true });
      return;
    }

    setLoading(true);
    try {
      const profile = await fetchCurrentUser();
      setUser(profile);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Authentication error";
      setError(message);
      setUser(null);
      localStorage.removeItem("access_token");
      navigate("/login", { replace: true });
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    void loadUser();
  }, [loadUser]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    navigate("/login", { replace: true });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-gray-600">Đang tải thông tin người dùng...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-gray-100">
      <aside className="w-64 bg-white shadow-md p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">QR Platform</h2>
        </div>
        <div className="rounded bg-gray-50 p-3 text-sm text-gray-600">
          {user ? (
            <>
              <div className="font-semibold">{user.email}</div>
              <div className="uppercase text-xs text-gray-500">{user.role}</div>
            </>
          ) : (
            <div>Không thể tải thông tin người dùng.</div>
          )}
        </div>
        {error ? <div className="text-sm text-red-600">{error}</div> : null}
        <nav className="space-y-2">
          <Link to="/" className="block p-2 hover:bg-gray-200 rounded">Dashboard</Link>
          <Link to="/qrcodes" className="block p-2 hover:bg-gray-200 rounded">QR Codes</Link>
          <Link to="/products" className="block p-2 hover:bg-gray-200 rounded">Products</Link>
          <Link to="/customers" className="block p-2 hover:bg-gray-200 rounded">Customers</Link>
          <Link to="/analytics" className="block p-2 hover:bg-gray-200 rounded">Analytics</Link>
        </nav>
        <button
          type="button"
          onClick={handleLogout}
          className="w-full rounded bg-red-500 px-3 py-2 text-sm font-medium text-white hover:bg-red-600"
        >
          Đăng xuất
        </button>
      </aside>

      <main className="flex-1 p-6">
        <Outlet context={{ user, refreshUser: loadUser }} />
      </main>
    </div>
  );
}
