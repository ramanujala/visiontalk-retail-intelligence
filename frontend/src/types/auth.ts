export interface Company {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface User {
  id: string;
  company_id: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'MANAGER' | 'STAFF';
  is_active: boolean;
  created_at: string;
  company?: Company;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
