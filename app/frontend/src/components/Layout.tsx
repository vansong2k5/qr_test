import { Link, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="min-h-screen flex bg-gray-100">

      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md p-4 space-y-4">
        <h2 className="text-xl font-bold mb-4">QR Platform</h2>

        <nav className="space-y-2">
          <Link to="/" className="block p-2 hover:bg-gray-200 rounded">Dashboard</Link>
          <Link to="/qrcodes" className="block p-2 hover:bg-gray-200 rounded">QR Codes</Link>
          <Link to="/products" className="block p-2 hover:bg-gray-200 rounded">Products</Link>
          <Link to="/customers" className="block p-2 hover:bg-gray-200 rounded">Customers</Link>
          <Link to="/analytics" className="block p-2 hover:bg-gray-200 rounded">Analytics</Link>
        </nav>
      </aside>

      {/* Content */}
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
