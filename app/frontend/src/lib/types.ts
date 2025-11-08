export type UserRole = "admin" | "staff";

export interface User {
  id: number;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface QrLifecycleEvent {
  id: number;
  qrcode_id: number;
  event_type: string;
  occurred_at: string;
  actor_id: number | null;
  metadata: Record<string, unknown> | null;
}

export interface QrCode {
  id: number;
  product_id: number;
  code: string;
  payload: Record<string, unknown> | null;
  reusable_mode: string;
  reuse_limit: number | null;
  reuse_count: number;
  lifecycle_policy: Record<string, unknown> | null;
  status: string;
  lifecycle_state: string;
  activated_at: string | null;
  retired_at: string | null;
  image_render_path: string | null;
  image_svg_path: string | null;
  image_mask_path: string | null;
  created_by: number;
  created_at: string;
  lifecycle_events: QrLifecycleEvent[];
}

export interface Product {
  id: number;
  customer_id: number;
  name: string;
  sku: string;
  description: string | null;
  lifecycle_status: string;
  created_at: string;
}
