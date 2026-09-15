export interface ImageItem {
  id: string;
  company_id: string;
  store_id: string;
  uploaded_by: string;
  original_filename: string;
  storage_key: string;
  mime_type: string;
  file_size: number;
  width: number;
  height: number;
  checksum: string;
  status: string;
  quality_score: number;
  quality_flags: string[];
  created_at: string;
  updated_at: string;
}

export interface ImageListResponse {
  items: ImageItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
