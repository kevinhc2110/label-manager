export interface Printer {
  id: string;
  name: string;
  ip_address: string;
  port: number;
  location: string;
  is_active: boolean;
}

export interface PrintLabelRequest {
  text: string;
  qr_data?: string;
  copies?: number;
}

export interface PrintLabelResponse {
  message: string;
  printer_id: string;
}

export interface PrinterHealth {
  printer_id: string;
  name: string;
  ip_address: string;
  port: number;
  is_online: boolean;
  latency_ms: number | null;
}
