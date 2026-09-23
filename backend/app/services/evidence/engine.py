"""Evidence Engine Service Layer.

Aggregates structured perception outputs (YOLO Detections and PaddleOCR Results) into a canonical,
deterministic Evidence snapshot with spatial relationships and cross-observation associations.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.image import Image, ImageStatus
from app.models.analysis import AnalysisRun, Detection, OCRResult, AnalysisRunStatus, AnalysisType
from app.services.detection.schemas import BoundingBox
from app.schemas.evidence import (
    CanonicalEvidenceResponse,
    EvidenceDetectionItem,
    EvidenceOCRItem,
    EvidenceMetadata
)
from app.services.evidence.spatial import (
    BoundingBox as SpatialBox,
    classify_spatial_relationship,
    calculate_overlap_ratio,
    calculate_center_distance
)
from app.services.evidence.exceptions import EvidenceNotFoundError, EvidenceGenerationError


EVIDENCE_VERSION = "1.0"


class EvidenceEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_canonical_evidence(
        self,
        image_id: UUID,
        company_id: UUID,
        overlap_threshold: float = 0.1,
        max_center_distance: float = 500.0
    ) -> CanonicalEvidenceResponse:
        """Generates canonical evidence aggregation for a specific image in a tenant.

        - Loads latest completed Detection AnalysisRun & OCR AnalysisRun
        - Normalizes observations into canonical evidence schemas
        - Computes deterministic spatial relationships between Detections and OCR text
        - Returns structured CanonicalEvidenceResponse
        """
        # 1. Verify Image Access & Tenant Ownership
        image = self.db.query(Image).filter(
            Image.id == image_id,
            Image.company_id == company_id,
            Image.status != ImageStatus.DELETED
        ).first()

        if not image:
            raise EvidenceNotFoundError("Image not found.")

        # 2. Fetch Latest Completed Object Detection Run
        det_run = self.db.query(AnalysisRun).filter(
            AnalysisRun.image_id == image_id,
            AnalysisRun.company_id == company_id,
            AnalysisRun.analysis_type == AnalysisType.OBJECT_DETECTION,
            AnalysisRun.status == AnalysisRunStatus.COMPLETED
        ).order_by(AnalysisRun.created_at.desc()).first()

        # 3. Fetch Latest Completed OCR Run
        ocr_run = self.db.query(AnalysisRun).filter(
            AnalysisRun.image_id == image_id,
            AnalysisRun.company_id == company_id,
            AnalysisRun.analysis_type == AnalysisType.OCR,
            AnalysisRun.status == AnalysisRunStatus.COMPLETED
        ).order_by(AnalysisRun.created_at.desc()).first()

        raw_detections: List[Detection] = det_run.detections if det_run and det_run.detections else []
        raw_ocr_results: List[OCRResult] = ocr_run.ocr_results if ocr_run and ocr_run.ocr_results else []

        # 4. Map OCR Results to Canonical Schema
        ocr_items: List[EvidenceOCRItem] = []
        ocr_spatial_map: dict[UUID, SpatialBox] = {}

        for ocr in raw_ocr_results:
            box = BoundingBox(
                x_min=ocr.x_min,
                y_min=ocr.y_min,
                x_max=ocr.x_max,
                y_max=ocr.y_max
            )
            item = EvidenceOCRItem(
                id=ocr.id,
                analysis_run_id=ocr.analysis_run_id,
                text=ocr.text,
                normalized_text=ocr.normalized_text,
                confidence=ocr.confidence,
                line_order=ocr.line_order,
                bounding_box=box
            )
            ocr_items.append(item)
            ocr_spatial_map[ocr.id] = SpatialBox(
                x_min=ocr.x_min,
                y_min=ocr.y_min,
                x_max=ocr.x_max,
                y_max=ocr.y_max
            )

        # 5. Map Detections to Canonical Schema & Calculate Spatial Associations
        detection_items: List[EvidenceDetectionItem] = []
        total_associations = 0

        for det in raw_detections:
            det_box = BoundingBox(
                x_min=det.x_min,
                y_min=det.y_min,
                x_max=det.x_max,
                y_max=det.y_max
            )
            det_spatial_box = SpatialBox(
                x_min=det.x_min,
                y_min=det.y_min,
                x_max=det.x_max,
                y_max=det.y_max
            )

            related_ocr_ids: List[UUID] = []
            spatial_rel_list: List[dict] = []

            for ocr_item in ocr_items:
                ocr_spatial_box = ocr_spatial_map[ocr_item.id]
                rel_metrics = classify_spatial_relationship(det_spatial_box, ocr_spatial_box)

                # Spatial Association Criterion: Overlap >= threshold OR (contained OR within reasonable center distance)
                if (
                    rel_metrics["ocr_overlap_ratio"] >= overlap_threshold
                    or rel_metrics["is_contained"] == 1.0
                    or rel_metrics["center_distance"] <= max_center_distance
                ):
                    related_ocr_ids.append(ocr_item.id)
                    spatial_rel_list.append({
                        "ocr_id": str(ocr_item.id),
                        "ocr_text": ocr_item.normalized_text,
                        "intersection_area": rel_metrics["intersection_area"],
                        "iou": rel_metrics["iou"],
                        "ocr_overlap_ratio": rel_metrics["ocr_overlap_ratio"],
                        "detection_overlap_ratio": rel_metrics["detection_overlap_ratio"],
                        "center_distance": rel_metrics["center_distance"],
                        "is_contained": bool(rel_metrics["is_contained"])
                    })

            total_associations += len(related_ocr_ids)

            detection_items.append(
                EvidenceDetectionItem(
                    id=det.id,
                    analysis_run_id=det.analysis_run_id,
                    class_id=det.class_id,
                    class_name=det.class_name,
                    confidence=det.confidence,
                    bounding_box=det_box,
                    related_ocr_ids=related_ocr_ids,
                    spatial_relationships=spatial_rel_list
                )
            )

        # 6. Build Evidence Metadata
        metadata = EvidenceMetadata(
            image_id=image_id,
            company_id=company_id,
            evidence_version=EVIDENCE_VERSION,
            total_detections=len(detection_items),
            total_ocr_regions=len(ocr_items),
            total_associations=total_associations,
            detection_run_id=det_run.id if det_run else None,
            ocr_run_id=ocr_run.id if ocr_run else None,
            generated_at=datetime.now(timezone.utc)
        )

        return CanonicalEvidenceResponse(
            image_id=image_id,
            company_id=company_id,
            evidence_version=EVIDENCE_VERSION,
            metadata=metadata,
            detections=detection_items,
            ocr_results=ocr_items
        )
