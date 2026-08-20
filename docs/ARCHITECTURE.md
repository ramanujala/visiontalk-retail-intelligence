# System Architecture — VisionTalk Retail Intelligence

## 1. Executive Summary

VisionTalk Retail Intelligence is designed as a **Modular Monolith** prioritizing correctness, auditability, performance, and explainability. Rather than relying on end-to-end black-box AI vision models, VisionTalk decomposes retail shelf analysis into three decoupled conceptual layers:

- **Layer 1: Perception** (YOLO Object Detection + PaddleOCR + OpenCV Preprocessing)
- **Layer 2: Structured Evidence** (Standardized JSON schema representing factual observations)
- **Layer 3: Reasoning & Explanation** (Deterministic Business Rules + Grounded Multimodal LLM)

This design ensures that counting, availability, placement, price verification, and compliance scores are computed using 100% deterministic algorithms, while the LLM is leveraged strictly for natural language synthesis, context generation, and grounded explanations.

---

## 2. High-Level System Architecture Diagram

```
                                  +-----------------------+
                                  |    React Frontend     |
                                  +-----------+-----------+
                                              | REST API (HTTP/JSON)
                                              v
                                  +-----------------------+
                                  |    FastAPI Backend    |
                                  +-----------+-----------+
                                              |
        +-------------------------------------+-------------------------------------+
        |                                     |                                     |
        v                                     v                                     v
+---------------+                     +---------------+                     +---------------+
| Image Service |                     |Analysis Engine|                     | Chat Service  |
+-------+-------+                     +-------+-------+                     +-------+-------+
        |                                     |                                     |
        | File Save                           v                                     |
        v                            Vision Orchestrator                            |
+---------------+                             |                                     |
| Storage Engine|                     +-------+-------+                             |
| (Local / S3)  |                     |               |                             |
+---------------+                     v               v                             v
                                  +-------+       +-------+                 +---------------+
                                  | YOLO  |       |  OCR  |                 |Question Router|
                                  +---+---+       +---+---+                 +-------+-------+
                                      |               |                             |
                                      +-------+-------+                             v
                                              |                             +---------------+
                                              v                             |  Gemini LLM   |
                                      +---------------+                     +---------------+
                                      |Evidence Engine|
                                      +-------+-------+
                                              |
                                              v
                                      +---------------+
                                      |Retail Analysis|
                                      +-------+-------+
                                              |
                                      +-------+-------+
                                      |               |
                                      v               v
                                +-----------+   +-----------+
                                |Compliance |   |Comparison |
                                +-----+-----+   +-----+-----+
                                      |               |
                                      +-------+-------+
                                              |
                                              v
                                      +---------------+
                                      | PostgreSQL DB |
                                      +---------------+
```

---

## 3. Layered Architectural Specifications

### 3.1 Layer 1 — Perception Engine
- **OpenCV**: Handles input image normalization, blur/glare quality validation, EXIF auto-rotation, and crop extraction.
- **YOLO (v8 / v11)**: Runs inference to detect product SKUs, shelf structures, price tags, and empty shelf regions. Outputs bounding boxes `(x1, y1, x2, y2)`, class IDs, and confidence scores.
- **PaddleOCR**: Extracts text snippets and bounding boxes from detected price tags and promotional shelf Talkers.

### 3.2 Layer 2 — Evidence Engine
- Normalizes raw model predictions into a versioned, canonical `Evidence` JSON structure.
- Assigns spatial coordinates `(x, y, level, shelf_index)` to detected items relative to shelf geometry.
- Stores model metadata (e.g., `detector_version: "yolo-retail-v1.0"`, `ocr_version: "paddleocr-v2.7"`).

### 3.3 Layer 3 — Business Reasoning & Grounded LLM
- **Expected vs Actual Engine**: Compares detected items against configured shelf planograms (expected SKUs, count targets).
- **Placement & Alignment Engine**: Computes spatial sequence compliance (e.g., SKU A must be left of SKU B).
- **Empty Shelf Detector**: Identifies spatial voids on shelf contours where products are absent.
- **Price Verification Engine**: Matches OCR extracted text against target pricing in the database.
- **Compliance Scoring Engine**: Computes an explainable weighted compliance index (0 - 100%).
- **Question Router & LLM**: Routes queries to deterministic engine methods first; passes structured evidence context to Google Gemini Flash for natural language summaries and step-by-step resolution advice.

---

## 4. Key Architectural Trade-offs & Decisions

| Decision | Selection | Rationale |
|---|---|---|
| **System Pattern** | Modular Monolith | Prevents network overhead & deployment complexity during early phases; easily extractable to microservices later. |
| **Counting / Availability** | Deterministic (YOLO Bounding Boxes) | LLMs hallucinate counts and fine-grained spatial coordinates; object detectors provide exact facts. |
| **Pricing / OCR** | PaddleOCR + Rule Parsing | Provides local fast inference and precise character bounding boxes. |
| **Explanation & Q&A** | Grounded Gemini LLM | Best-in-class natural language generation and multimodal context understanding when constrained by evidence. |
| **Database** | PostgreSQL | Robust transactional integrity, JSONB support for evidence/configurations, and standard relational modeling. |

---

## 5. Security Architecture & Guardrails

1. **Prompt Injection Defense**: User queries sent to the Question Router are strictly delimited and wrapped in structured templates. System instructions prohibit acting on commands inside evidence text or user prompts that request breaking grounding constraints.
2. **Storage Isolation**: Images are stored with randomized UUID filenames; direct path traversing is forbidden.
3. **Data Protection**: Sensitive credentials (API keys, database URLs, JWT secrets) are loaded strictly via `.env` environment variables and NEVER hardcoded or checked into source control.
4. **Input Sanitation**: Uploaded files are validated for MIME type, image header signatures, and max size limit (20MB).

---

## 6. Scalability & Evolution Roadmap

- **Phase 1-17**: Single FastAPI process with synchronous/in-process pipeline execution for low latency and easy debugging.
- **Phase 18+**: Integration of Redis message broker + Celery worker pool for non-blocking asynchronous analysis execution on GPU/CPU workers.
- **Production Storage**: Seamless swap from `LocalStorageProvider` to `S3StorageProvider` (MinIO/AWS S3) via repository abstraction.
