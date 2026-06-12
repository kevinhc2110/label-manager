export interface Printer {
  id: string;
  name: string;
  ip_address: string;
  port: number;
  location: string;
  is_active: boolean;
}

export interface PrintLabelResponse {
  message: string;
  printer_id: string;
}
