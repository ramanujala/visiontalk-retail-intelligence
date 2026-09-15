export interface Store {
  id: string;
  company_id: string;
  name: string;
  code: string;
  location?: string;
  is_active: boolean;
  created_at: string;
}

export interface StoreCreatePayload {
  name: string;
  code: string;
  location?: string;
}
