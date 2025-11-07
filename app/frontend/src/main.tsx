import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./index.css";

import Layout from "./components/Layout";

import { Dashboard } from "./pages/Dashboard";
import { Customers } from "./pages/Customers";
import { Products } from "./pages/Products";
import { QRCodes } from "./pages/QRCodes";
import { Analytics } from "./pages/Analytics";
import { Login } from "./pages/Login";

const App = () => (
  <BrowserRouter>
    <Routes>

      {/* Trang Login tách riêng */}
      <Route path="/login" element={<Login />} />

      {/* Các trang admin nằm trong Layout */}
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/customers" element={<Customers />} />
        <Route path="/products" element={<Products />} />
        <Route path="/qrcodes" element={<QRCodes />} />
        <Route path="/analytics" element={<Analytics />} />
      </Route>

    </Routes>
  </BrowserRouter>
);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

