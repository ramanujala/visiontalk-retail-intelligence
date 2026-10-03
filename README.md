# VisionTalk Retail Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-blue.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)

An enterprise-grade, AI-powered retail visual intelligence platform that converts store shelf images into structured, deterministic, and explainable retail operational insights.

---

## 🚦 Project Status

- [x] **Phase 0 — Architecture & Planning**: Architecture design, database schema, API contract, ML strategy, and guidelines documented.
- [x] **Phase 1 — Project Foundation**: Modular FastAPI backend, React 18 + TypeScript frontend shell, PostgreSQL configuration, StorageService abstraction, health check endpoints (liveness & readiness), Docker Compose setup, and Pytest/Vitest testing suites.
- [x] **Phase 2 — Multi-Tenant Foundation & Authentication**: Relational domain models (`Company`, `User`, `Store`), Alembic database migrations, bcrypt password hashing, JWT authentication, atomic company registration, strict backend tenant isolation, role authorization, tenant Store APIs, React authentication UI, and comprehensive Pytest/Vitest test suites.
- [x] **Phase 3 — Image Ingestion, Validation & Storage**: Image model (`Image`), Alembic migration (`002_phase3_images_schema`), image upload API (`POST /api/v1/images`), MIME/header/dimension/size file validation, Pillow decoding check, SHA-256 checksum generation, deterministic OpenCV image quality assessment (score & flags), secure storage pathing (`{company_id}/{store_id}/{uuid}.jpg`), tenant-isolated listing/detail/deletion APIs, React ImageUpload UI, and comprehensive Pytest/Vitest tests.
- [x] **Phase 4 — Object Detection Pipeline (Perception Layer)**: Ultralytics YOLO baseline integration, modular lazy model loader (`get_yolo_model`), `AnalysisRun` and `Detection` database models, Alembic migration (`003_phase4_object_detection_schema`), synchronous detection workflow (`POST /api/v1/detections/analyze/{image_id}`), tenant isolation enforcement, duplicate analysis prevention, REST APIs for analysis details/summaries, responsive React `DetectionOverlay` bounding box visualizer, and comprehensive Pytest/Vitest test suites.
- [x] **Phase 5 — OCR & Text Extraction Pipeline (Text Perception)**: PaddleOCR engine integration, lazy model loader (`get_paddle_ocr_engine`), `OCRResult` database model, Alembic migration (`004_phase5_ocr_schema`), synchronous text extraction workflow (`POST /api/v1/ocr/analyze/{image_id}`), deterministic whitespace normalization, tenant isolation enforcement, duplicate analysis reuse, REST APIs (`/api/v1/ocr`), responsive React `OCROverlay` bounding box visualizer & `OCRView`, and comprehensive Pytest/Vitest test suites.
- [x] **Phase 6 — Evidence Engine (Normalization & Aggregation)**: Deterministic spatial utilities (`BoundingBox`, IoU, overlap ratio, containment, center distance), canonical Pydantic schemas (`CanonicalEvidenceResponse`), `EvidenceEngine` domain service, multi-tenant Evidence API (`/api/v1/evidence`), deterministic detection-OCR spatial association, versioned canonical snapshots (`1.0`), React `EvidenceOverlay` & `EvidenceView`, and comprehensive Pytest/Vitest test suites.
- [x] **Phase 7 — Expected vs Actual Analysis (Structured Reasoning)**: `ExpectedProduct` ORM model, Alembic migration (`005_phase7_expected_actual_schema`), Expected Products CRUD API (`/api/v1/expected-products`), deterministic matching strategy, comparison status evaluation (`OBSERVED`, `MISSING`, `LOW_STOCK`, `EXCESS`, `UNEXPECTED`, `UNMATCHED`), explainable issue generation, evidence traceability, Expected vs Actual API (`/api/v1/analysis/expected-vs-actual`), React `ExpectedProductManager` & `ExpectedActualView`, and comprehensive Pytest/Vitest test suites.
- [x] **Phase 8 — Retail Compliance Rules Engine**: `ComplianceRule` and `ComplianceFinding` ORM models, Alembic migration (`006_phase8_compliance_rules_schema`), Rule CRUD API (`/api/v1/compliance-rules`), Compliance Engine service, deterministic rule evaluation (`PRODUCT_REQUIRED`, `PRODUCT_QUANTITY`, `UNEXPECTED_PRODUCT`, `PRODUCT_ZONE`, `OCR_REQUIRED`, `CUSTOM_THRESHOLD`), severity levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), structured findings & deterministic messages, full evidence traceability, Compliance API (`/api/v1/compliance`), React `ComplianceRuleManager` & `ComplianceView`, strict multi-tenant isolation & RBAC, and comprehensive Pytest/Vitest test suites.
- [x] **Phase 9 — Gemini / Vision LLM Integration**: Official `google-genai` SDK wrapper (`LLMService`), Pydantic settings configuration (`GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_ENABLED`), sanitized context builder (`build_grounded_llm_context`), strict grounding prompt builder (`build_grounding_prompt`), low-confidence fallback handling, prompt injection defense isolating untrusted OCR evidence text, REST explanation APIs (`/api/v1/llm`), React `AIExplanationView` component & card action buttons, strict multi-tenant isolation, and comprehensive Pytest/Vitest test suites.
- [x] **Phase 10 — Question Router Architecture**: Strategy pattern intent classifier (`IntentClassifier`), question router service (`QuestionRouter`), typed question intents (`COUNT`, `AVAILABILITY`, `EXPECTED_VS_ACTUAL`, `COMPLIANCE`, `GENERAL`, `UNKNOWN`), deterministic pattern-matching rules, fallback routing to grounded LLM service, REST routing endpoint (`POST /api/v1/questions/route`), strict multi-tenant image access validation, and comprehensive Pytest test suite.

---

## 🏗️ System Architecture & Layer Breakdown

VisionTalk decomposes retail shelf analysis into decoupled conceptual layers:

```
+-----------------------------------------------------------------------+
|                         LAYER 1: PERCEPTION                           |
|  YOLO (Objects & Boxes)  |  PaddleOCR (Text & Price)  | OpenCV (Image) |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                          LAYER 2: EVIDENCE                            |
|       Evidence Engine: Normalization, Spatial Relationships &         |
|     Canonical JSON Snapshot (No Business/LLM Decisions Performed)     |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                      LAYER 3: EXPECTED VS ACTUAL                      |
|  Phase 7: Deterministic Inventory Comparison & Discrepancy Tracking   |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                 LAYER 4: COMPLIANCE RULES ENGINE                      |
|   Phase 8: Business Rule Checks (Required, Quantity, Zone, OCR),      |
|    Severity Grading & Traceable Findings (Strictly Deterministic)     |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                      LAYER 5: AI REASONING (FUTURE)                    |
|       Future: Grounded Multimodal LLM (Gemini 2.5/3 Flash)            |
+-----------------------------------------------------------------------+
```

### Evidence & Reasoning Layer Principles

> **Note**: Phase 7 performs deterministic comparison between configured store expectations and structured observations from the Evidence Layer. It does not use LLM reasoning or semantic product matching.

1. **Observations Preservation**: Raw class names, bounding boxes, text strings, and confidences are preserved without lossy transformation.
2. **Deterministic Matching**: Evaluates exact normalized product codes and names against active expectations without guessing or LLM hallucinations.
3. **Structured Discrepancies**: Emits precise inventory comparison statuses (`OBSERVED`, `MISSING`, `LOW_STOCK`, `EXCESS`, `UNEXPECTED`, `UNMATCHED`) and actionable issues (`MISSING_PRODUCT`, `LOW_STOCK`, etc.).
4. **Full Traceability**: Every generated item and issue preserves direct JSON evidence references back to underlying object detections and OCR text regions.
5. **Tenant Isolation**: Every expectation CRUD and analysis endpoint strictly verifies `company_id == current_user.company_id`.

For detailed specs, refer to:
- [docs/ARCHITECTURE.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/ARCHITECTURE.md)
- [docs/ROADMAP.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/ROADMAP.md)
- [docs/API_DESIGN.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/API_DESIGN.md)
- [docs/DATA_MODEL.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/DATA_MODEL.md)

---

## 🔐 Multi-Tenant Identity & Access Architecture

```
Company (Tenant)
  ├── Users (ADMIN, MANAGER, STAFF)
  └── Stores (Tenant Isolated Locations)
```

1. **Strict Backend Tenant Isolation**: Every query execution at the backend database layer enforces `company_id == current_user.company_id`. Attempts to access another company's store or resource return `404 Not Found` to prevent leaking cross-tenant data.
2. **Atomic Registration**: `POST /api/v1/auth/register` creates the `Company` tenant and its primary `ADMIN` user inside a single database transaction.
3. **JWT Authentication**: Bearer tokens are signed via environment `JWT_SECRET_KEY` and carry `sub: user_id`, `company_id`, and `role` claims.

---

## 🛠️ Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+ (with npm)
- **PostgreSQL**: 15+ (Local or Docker)
- **Docker & Docker Compose** (Optional for containerized development)

---

## 🚀 Local Setup & Getting Started

### 1. Environment Configuration
Copy the template `.env.example` file to `.env`:
```bash
cp .env.example .env
```

### 2. Database Migrations (Alembic)
Apply database migrations to set up PostgreSQL tables:
```bash
cd backend
alembic upgrade head
```

### 3. Backend Setup & Local Server
Create a virtual environment, install dependencies, and launch FastAPI:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r backend/requirements.txt

# Run FastAPI server
cd backend
uvicorn app.main:app --reload --port 8000
```
Backend will be available at `http://localhost:8000`. API documentation is accessible at `http://localhost:8000/api/v1/docs`.

### 4. Frontend Setup & React Shell
Install npm packages and launch Vite development server:
```bash
cd frontend
npm install
npm run dev
```
Frontend application will be accessible at `http://localhost:5173`.

---

## 🐳 Docker Compose Setup

Spin up PostgreSQL, FastAPI backend, and React frontend containers in a single command:
```bash
docker compose up -d --build
```
- **Frontend App**: `http://localhost:5173`
- **FastAPI Backend**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432`

---

## 🧪 Testing Protocols

### Backend Pytest Suite
Run unit and tenant-isolation integration tests:
```bash
cd backend
pytest
```

### Frontend Vitest Suite
Run React component unit tests:
```bash
cd frontend
npm test
```

---

## 📄 License

This project is licensed under the MIT License.
