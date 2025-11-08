export interface QrCode {
  code_id: string
  product_id?: number
  customer_id?: number
  reuse_allowed: boolean
  reuse_cycle: number
  active: boolean
  version: number
  ecc: string
  image_url_png: string
  image_url_svg: string
  created_at: string
  updated_at: string
}

export interface Customer {
  id: number
  name: string
  email?: string
  phone?: string
}

export interface Product {
  id: number
  name: string
  sku: string
  owner_customer_id?: number
}

export interface ScanEvent {
  id: number
  ts: string
  device?: string
  approx_geo?: string
}
