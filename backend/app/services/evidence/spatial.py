"""Spatial relationship and geometric calculation utilities.
Provides deterministic bounding box overlap, intersection, IoU, containment, center distance, and nearest-neighbor calculations.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel


class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return max(0.0, self.x_max - self.x_min)

    @property
    def height(self) -> float:
        return max(0.0, self.y_max - self.y_min)

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> Tuple[float, float]:
        return (
            (self.x_min + self.x_max) / 2.0,
            (self.y_min + self.y_max) / 2.0
        )


def calculate_intersection_area(box1: BoundingBox, box2: BoundingBox) -> float:
    """Calculates absolute pixel/coordinate area of intersection between two boxes."""
    inter_x_min = max(box1.x_min, box2.x_min)
    inter_y_min = max(box1.y_min, box2.y_min)
    inter_x_max = min(box1.x_max, box2.x_max)
    inter_y_max = min(box1.y_max, box2.y_max)

    inter_w = max(0.0, inter_x_max - inter_x_min)
    inter_h = max(0.0, inter_y_max - inter_y_min)

    return inter_w * inter_h


def calculate_iou(box1: BoundingBox, box2: BoundingBox) -> float:
    """Calculates Intersection-over-Union (IoU) ratio between two bounding boxes."""
    inter_area = calculate_intersection_area(box1, box2)
    if inter_area <= 0.0:
        return 0.0
    union_area = box1.area + box2.area - inter_area
    if union_area <= 0.0:
        return 0.0
    return round(inter_area / union_area, 4)


def calculate_overlap_ratio(source_box: BoundingBox, target_box: BoundingBox) -> float:
    """Calculates fraction of source_box's area that overlaps with target_box (Intersection / Area(source_box))."""
    source_area = source_box.area
    if source_area <= 0.0:
        return 0.0
    inter_area = calculate_intersection_area(source_box, target_box)
    return round(inter_area / source_area, 4)


def calculate_containment(inner_box: BoundingBox, outer_box: BoundingBox) -> bool:
    """Returns True if inner_box is strictly or loosely inside outer_box boundaries."""
    return (
        inner_box.x_min >= outer_box.x_min and
        inner_box.y_min >= outer_box.y_min and
        inner_box.x_max <= outer_box.x_max and
        inner_box.y_max <= outer_box.y_max
    )


def calculate_center_distance(box1: BoundingBox, box2: BoundingBox) -> float:
    """Calculates Euclidean distance between centers of box1 and box2."""
    c1_x, c1_y = box1.center
    c2_x, c2_y = box2.center
    dx = c1_x - c2_x
    dy = c1_y - c2_y
    return round((dx * dx + dy * dy) ** 0.5, 4)


def classify_spatial_relationship(
    detection_box: BoundingBox,
    ocr_box: BoundingBox
) -> Dict[str, float]:
    """Computes comprehensive spatial relationship metrics between a detection box and an OCR box."""
    inter_area = calculate_intersection_area(detection_box, ocr_box)
    iou = calculate_iou(detection_box, ocr_box)
    ocr_overlap = calculate_overlap_ratio(ocr_box, detection_box)
    det_overlap = calculate_overlap_ratio(detection_box, ocr_box)
    center_dist = calculate_center_distance(detection_box, ocr_box)
    is_contained = calculate_containment(ocr_box, detection_box)

    return {
        "intersection_area": inter_area,
        "iou": iou,
        "ocr_overlap_ratio": ocr_overlap,
        "detection_overlap_ratio": det_overlap,
        "center_distance": center_dist,
        "is_contained": 1.0 if is_contained else 0.0
    }
