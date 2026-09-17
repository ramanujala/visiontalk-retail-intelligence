import os
from typing import List, Tuple
from PIL import Image as PILImage

from app.core.config import settings
from app.services.detection.model import get_yolo_model
from app.services.detection.schemas import DetectionEvidence, DetectionResult, BoundingBox
from app.services.detection.exceptions import InferenceError


class ObjectDetectionService:
    """Service handling Ultralytics YOLO inference and normalizing outputs into structured evidence."""

    def __init__(self, confidence_threshold: float = None, iou_threshold: float = None, device: str = None):
        self.conf_thresh = confidence_threshold if confidence_threshold is not None else settings.YOLO_CONFIDENCE_THRESHOLD
        self.iou_thresh = iou_threshold if iou_threshold is not None else settings.YOLO_IOU_THRESHOLD
        self.device = device if device is not None else settings.YOLO_DEVICE

    def detect_objects(self, image_path: str) -> DetectionEvidence:
        """Executes YOLO object detection on the given image path and returns structured evidence."""
        if not os.path.exists(image_path):
            raise InferenceError(f"Image file does not exist at path: {image_path}")

        # Get original image dimensions
        try:
            with PILImage.open(image_path) as img:
                img_width, img_height = img.size
        except Exception as img_err:
            raise InferenceError(f"Failed to read image dimensions: {str(img_err)}")

        # Run inference
        try:
            model = get_yolo_model()
            results = model.predict(
                source=image_path,
                conf=self.conf_thresh,
                iou=self.iou_thresh,
                device=self.device,
                verbose=False
            )
        except Exception as err:
            raise InferenceError(f"YOLO inference execution failed: {str(err)}")

        detections: List[DetectionResult] = []

        if results and len(results) > 0:
            boxes = results[0].boxes
            names = results[0].names  # Class ID -> name map

            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    # Extract coordinates (x_min, y_min, x_max, y_max)
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    cls_name = str(names.get(cls_id, f"class_{cls_id}"))

                    detections.append(
                        DetectionResult(
                            class_id=cls_id,
                            class_name=cls_name,
                            confidence=round(conf, 4),
                            bbox=BoundingBox(
                                x_min=round(float(xyxy[0]), 2),
                                y_min=round(float(xyxy[1]), 2),
                                x_max=round(float(xyxy[2]), 2),
                                y_max=round(float(xyxy[3]), 2)
                            )
                        )
                    )

        return DetectionEvidence(
            image_width=img_width,
            image_height=img_height,
            total_detections=len(detections),
            detections=detections
        )
