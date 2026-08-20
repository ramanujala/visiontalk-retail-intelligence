# Machine Learning Strategy — VisionTalk Retail Intelligence

## 1. Vision Strategy Overview

VisionTalk Retail Intelligence leverages a hybrid AI computer vision architecture:
1. **Pre-trained Object Detection Baseline** (YOLOv8/YOLOv11 COCO pre-trained) for immediate Phase 4 prototyping.
2. **Domain-Specific Fine-Tuning** on retail shelf datasets (SKU detection, shelf boundaries, price tags, empty gaps) for Phase 15.
3. **PaddleOCR** for text and price extraction.
4. **Google Gemini LLM** via official Google GenAI SDK for grounded natural language synthesis.

---

## 2. Object Detection Pipeline (YOLO)

### 2.1 Model Selection & Justification
- **Architecture**: Ultralytics YOLOv8 / YOLOv11 (Small/Medium variants).
- **Rationale**: Real-time inference speed (15-30ms on GPU, 100-250ms on CPU), high precision on small retail items, and native PyTorch/ONNX export support.

### 2.2 Pre-trained Baseline (Phases 4-13)
- Utilizes pre-trained COCO weights to detect generic retail categories (e.g., `bottle`, `can`, `box`, `cell phone`).
- Validates end-to-end evidence pipelines, database persistence, compliance logic, and frontend visualization before custom model training.

### 2.3 Custom Retail Fine-Tuning (Phases 14-15)
- **Target Classes**:
  1. `product_sku` (Individual retail SKUs)
  2. `price_tag` (Shelf price labels)
  3. `empty_shelf_space` (Gaps on shelf)
  4. `shelf_divider` / `shelf_rail` (Physical shelf structure)
  5. `promo_sign` (Promotional displays)
- **Data Augmentation Strategy**:
  - Random brightness / contrast adjustments (simulates poor store lighting).
  - Subtle perspective and scaling transformations.
  - No aggressive flips that reverse readable text on packages.

---

## 3. Optical Character Recognition (PaddleOCR)

### 3.1 OCR Pipeline Workflow
```
Full Image -> Price Tag BBox (from YOLO) -> Crop Image -> Preprocessing (Grayscale + Threshold) -> PaddleOCR -> Text & Confidence
```

### 3.2 Post-Processing & Parsing
- Extracted text strings are parsed using regular expressions for currency symbols and numeric patterns:
  - Currency patterns: `₹\s*\d+(?:\.\d{2})?`, `\$\s*\d+(?:\.\d{2})?`, `\d+\s*INR`
  - Unit price / barcode patterns.
- OCR confidence scores below `0.60` are flagged as uncertain in structured evidence.

---

## 4. Model Versioning & Registry Strategy

Every analysis execution records the exact model identifiers:
```json
{
  "model_versions": {
    "detector_name": "yolo-retail-v1.2",
    "detector_weights": "weights/yolo_retail_v1.2.pt",
    "ocr_engine": "paddleocr-v2.7",
    "llm_model": "gemini-2.5-flash"
  }
}
```
Models are stored under `backend/app/models/weights/` with semantic versioning tag tracking.

---

## 5. Hardware & Resource Execution Profile

| Processing Environment | Inference Speed (YOLO) | OCR Speed (PaddleOCR) | Total Latency |
|---|---|---|---|
| **CPU Only (Development)** | ~180 ms | ~350 ms | ~550 ms |
| **GPU (NVIDIA T4 / RTX 3060)** | ~25 ms | ~80 ms | ~105 ms |

Unit tests must execute without requiring GPU access by mocking model outputs or using tiny light CPU weights.
