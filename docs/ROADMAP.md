# Development Roadmap — VisionTalk Retail Intelligence

This document details the 20 distinct execution phases of VisionTalk Retail Intelligence. Each phase must be executed sequentially and completely before advancing to the next.

---

## 📅 Execution Phases

### 📍 PHASE 0: Architecture & Planning (COMPLETED)
- **Goal**: Define problem statement, technical stack, system architecture, database models, API specs, ML strategy, and guidelines.
- **Deliverables**: `README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/ML_STRATEGY.md`, `docs/API_DESIGN.md`, `docs/DATA_MODEL.md`, `docs/RETAIL_ANALYSIS.md`, `docs/LLM_GROUNDING.md`, `docs/EVALUATION.md`, `docs/DEVELOPMENT_GUIDELINES.md`.

---

### 📍 PHASE 1: Project Foundation
- **Goal**: Initialize clean backend (FastAPI) and frontend (React + TypeScript + CSS Modules) monorepo structure.
- **Deliverables**: Working FastAPI server with health check, React app shell with basic routing, linting/formatting configs, and basic unit test runner.

---

### 📍 PHASE 2: Authentication + Company + Store Management
- **Goal**: Build tenant hierarchy and user authentication.
- **Deliverables**: JWT authentication API (`/login`, `/register`), PostgreSQL database setup, SQLAlchemy models for Users, Companies, Stores, and CRUD endpoints.

---

### 📍 PHASE 3: Image Upload & Storage Management
- **Goal**: Implement secure retail shelf image ingestion.
- **Deliverables**: Image upload endpoint (`/api/v1/images/upload`), image metadata database model, Local/S3 storage abstraction, image validation (MIME, size, EXIF rotation).

---

### 📍 PHASE 4: YOLO Object Detection Integration
- **Goal**: Build Layer 1 object detection service using Ultralytics YOLO.
- **Deliverables**: `VisionService` using pre-trained YOLO, object detection wrapper, bounding box coordinate normalization, detection schemas, and test suite with sample retail images.

---

### 📍 PHASE 5: OCR Integration
- **Goal**: Implement text and price extraction from shelf images.
- **Deliverables**: `OCRService` using PaddleOCR, bounding box localization for shelf tags, text filtering/cleaning heuristics, and pricing text parser.

---

### 📍 PHASE 6: Evidence Engine
- **Goal**: Combine YOLO and OCR outputs into canonical, versioned JSON evidence.
- **Deliverables**: `EvidenceEngine`, standardized JSON schema, spatial indexing logic (shelf level / relative positions), DB persistence for `AnalysisRun`, `Detections`, and `OCRResults`.

---

### 📍 PHASE 7: Expected vs Actual Retail Analysis
- **Goal**: Implement planogram compliance matching logic.
- **Deliverables**: `ExpectedProducts` database model, deterministic comparison engine (`AvailabilityEngine`), missing product finder, extra product finder, item counting logic.

---

### 📍 PHASE 8: Compliance Scoring Engine
- **Goal**: Implement explainable, multi-factor shelf compliance scoring.
- **Deliverables**: Configurable weights for availability (40%), placement (25%), price (15%), condition (10%), image quality (10%); math verification tests; visual break-down breakdown breakdown breakdown.

---

### 📍 PHASE 9: Gemini / Vision LLM Integration
- **Goal**: Implement grounded natural language explanation generation using Google GenAI SDK.
- **Deliverables**: `LLMService` wrapper using official `google-genai` SDK, grounding prompt builder, context injector, fallback handling for low confidence.

---

### 📍 PHASE 10: Question Router Architecture
- **Goal**: Implement clean strategy pattern router for incoming user queries.
- **Deliverables**: `QuestionRouter`, routing rules for count queries, availability, pricing, compliance, change analysis, and complex natural language reasoning.

---

### 📍 PHASE 11: Conversation System
- **Goal**: Enable multi-turn chat regarding retail analysis runs.
- **Deliverables**: `Conversations` & `Messages` schema, chat endpoints (`/api/v1/chat`), chat UI in React dashboard with grounded message history.

---

### 📍 PHASE 12: Image Comparison (Before vs After)
- **Goal**: Enable audit comparisons between store visits.
- **Deliverables**: `ComparisonService`, evidence delta calculator (added/removed items, price changes), visual side-by-side diffing in frontend dashboard.

---

### 📍 PHASE 13: Human Feedback & Verification Loop
- **Goal**: Collect store employee feedback on AI predictions.
- **Deliverables**: `Feedback` DB schema, UI confirmation/correction actions (Confirm/Incorrect), dataset logging for continuous improvement.

---

### 📍 PHASE 14: Retail Dataset Collection & Curation
- **Goal**: Prepare retail image pipeline for custom fine-tuning.
- **Deliverables**: Dataset directory structure, annotation schema export scripts (YOLO format), validation scripts for box coordinates and classes.

---

### 📍 PHASE 15: Custom YOLO Fine-Tuning Pipeline
- **Goal**: Train custom YOLO model on retail shelf classes.
- **Deliverables**: Model training scripts (`train.py`), hyperparameter configs, evaluation script, export script to ONNX/PyTorch.

---

### 📍 PHASE 16: Model Evaluation & Error Analysis
- **Goal**: Rigorously benchmark computer vision and LLM outputs.
- **Deliverables**: Evaluation pipeline computing mAP@50, mAP@50-95, Precision, Recall, OCR accuracy, LLM groundedness metrics, confusion matrix generator.

---

### 📍 PHASE 17: Model Versioning & Registry
- **Goal**: Manage model lifecycles and seamless upgrades.
- **Deliverables**: Model version registry in DB, dynamic model loader, metadata logging per analysis run.

---

### 📍 PHASE 18: Redis & Async Background Worker Processing
- **Goal**: Decouple heavy CV/OCR inference from API requests.
- **Deliverables**: Redis task queue integration, background workers for image processing, status polling endpoint (`/analysis/{id}/status`).

---

### 📍 PHASE 19: Docker & CI/CD Setup
- **Goal**: Containerize application and setup automated testing.
- **Deliverables**: `Dockerfile` for backend and frontend, `docker-compose.yml`, GitHub Actions workflow for linting, testing, and security scanning.

---

### 📍 PHASE 20: Production Hardening & Documentation Finalization
- **Goal**: Ensure production readiness, security audit, and final demonstration polish.
- **Deliverables**: Rate limiting, security headers, logging setup, final performance benchmarks, major project demo guide.
