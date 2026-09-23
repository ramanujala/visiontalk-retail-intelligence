export interface EvidenceBoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface SpatialRelationship {
  ocr_id: string;
  ocr_text: string;
  intersection_area: number;
  iou: number;
  ocr_overlap_ratio: number;
  detection_overlap_ratio: number;
  center_distance: number;
  is_contained: boolean;
}

export interface EvidenceDetectionItem {
  id: string;
  analysis_run_id: string;
  class_id: number;
  class_name: string;
  confidence: number;
  bounding_box: EvidenceBoundingBox;
  related_ocr_ids: string[];
  spatial_relationships: SpatialRelationship[];
}

export interface EvidenceOCRItem {
  id: string;
  analysis_run_id: string;
  text: string;
  normalized_text: string;
  confidence: number;
  line_order: number;
  bounding_box: EvidenceBoundingBox;
}

export interface EvidenceMetadata {
  image_id: string;
  company_id: string;
  evidence_version: string;
  total_detections: number;
  total_ocr_regions: number;
  total_associations: number;
  detection_run_id?: string;
  ocr_run_id?: string;
  generated_at: string;
}

export interface CanonicalEvidenceResponse {
  image_id: string;
  company_id: string;
  evidence_version: string;
  metadata: EvidenceMetadata;
  detections: EvidenceDetectionItem[];
  ocr_results: EvidenceOCRItem[];
}
