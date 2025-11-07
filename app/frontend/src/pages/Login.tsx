export const Login = () => (
  <div className="min-h-screen flex items-center justify-center bg-slate-100">
    <form className="bg-white p-6 rounded shadow w-80 space-y-4">
      <h1 className="text-xl font-semibold">Sign in</h1>
      <input className="w-full border rounded px-3 py-2" placeholder="Email" type="email" />
      <input className="w-full border rounded px-3 py-2" placeholder="Password" type="password" />
      <button className="w-full bg-blue-600 text-white py-2 rounded">Login</button>
    </form>
  </div>
);
