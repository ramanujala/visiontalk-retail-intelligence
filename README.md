# VisionTalk Retail Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![YOLO](https://img.shields.io/badge/YOLO-v8%2Fv11-orange.svg)](https://docs.ultralytics.com/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-v2.7+-red.svg)](https://github.com/PaddlePaddle/PaddleOCR)

An enterprise-grade, AI-powered retail visual intelligence platform that converts store shelf images into structured, deterministic, and explainable retail operational insights.

---

## 📌 Executive Overview

Retail shelf auditing is traditionally manual, expensive, error-prone, and difficult to scale across store networks. **VisionTalk Retail Intelligence** automates shelf inspection by systematically answering critical operational questions:

1. What products are present on the shelf?
2. How many items of each SKU exist?
3. Which expected products are missing or misplaced?
4. Are there unauthorized extra products?
5. Are there empty shelf gaps requiring replenishment?
6. Are displayed promotional prices matching expected store pricing?
7. What is the overall compliance score of the shelf?
8. What specific visual changes occurred compared to a prior visit?

---

## 🏗️ Core Architectural Principle

VisionTalk strictly avoids being a simple "image-to-LLM" chatbot. It separates intelligence into three deterministic, audit-traceable layers:

```
+-----------------------------------------------------------------------+
|                         LAYER 1: PERCEPTION                           |
|  YOLO (Objects & Boxes)  |  PaddleOCR (Text & Price)  | OpenCV (Image) |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                          LAYER 2: EVIDENCE                            |
|             Structured JSON Evidence (Bounding BBoxes,                |
|           Spatial Coordinates, Text Confidence, Signatures)           |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                          LAYER 3: REASONING                           |
|   Deterministic Rules (Expected vs Actual, Placement, Gaps, Price)    |
|                                   +                                   |
|            Grounded Multimodal LLM (Gemini 2.5/3 Flash)               |
+-----------------------------------------------------------------------+
```

1. **Perception**: Computer vision models extract factual visual attributes (bounding boxes, class labels, text, spatial positions).
2. **Evidence**: Formats raw perceptual outputs into a strictly typed, versioned structured JSON evidence schema.
3. **Reasoning**: Applies deterministic business algorithms for counts, missing products, placement verification, and price discrepancies, using LLM ONLY for grounded natural language explanations.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Vanilla CSS (Design Tokens & CSS Modules)
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Computer Vision**: Ultralytics YOLO, OpenCV
- **OCR**: PaddleOCR
- **Multimodal AI**: Google GenAI SDK (Gemini 2.5 / 3 Flash)
- **Storage**: Abstracted Storage Provider (Local Filesystem for Dev, S3-compatible for Prod)
- **Background & Caching**: Redis + Celery / Worker Queue (Architecture Ready)
- **Containerization**: Docker, Docker Compose
- **Testing**: Pytest (Backend/CV), Vitest / React Testing Library (Frontend)

---

## 📂 Repository Layout

```
visiontalk-retail-intelligence/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md          # End-to-end system design & data flow
│   ├── ROADMAP.md               # 20-Phase implementation plan
│   ├── ML_STRATEGY.md           # CV/OCR/YOLO fine-tuning strategy
│   ├── API_DESIGN.md            # REST API contract specifications
│   ├── DATA_MODEL.md            # Database schema & Evidence JSON schema
│   ├── RETAIL_ANALYSIS.md       # Deterministic business logic & math
│   ├── LLM_GROUNDING.md         # Prompting & grounding guardrails
│   ├── EVALUATION.md            # CV, OCR, and LLM metrics & benchmarks
│   └── DEVELOPMENT_GUIDELINES.md # Code standards, git rules, & security
├── backend/                     # FastAPI Application (Phase 1+)
└── frontend/                    # React Application (Phase 1+)
```

---

## 🚦 Project Status

Current Phase: **PHASE 0 — Architecture & Planning Complete**

Refer to [docs/ROADMAP.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/ROADMAP.md) for the complete 20-phase execution plan.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
