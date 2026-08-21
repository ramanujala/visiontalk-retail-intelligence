# VisionTalk Retail Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-blue.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)

An enterprise-grade, AI-powered retail visual intelligence platform that converts store shelf images into structured, deterministic, and explainable retail operational insights.

---

## 🚦 Project Status: PHASE 1 COMPLETE

- [x] **Phase 0 — Architecture & Planning**: Architecture design, database schema, API contract, ML strategy, and guidelines documented.
- [x] **Phase 1 — Project Foundation**: Modular FastAPI backend, React 18 + TypeScript frontend shell, PostgreSQL configuration, StorageService abstraction, health check endpoints (liveness & readiness), Docker Compose setup, and Pytest/Vitest testing suites.

---

## 🏗️ System Architecture & Layer Breakdown

VisionTalk decomposes retail shelf analysis into three decoupled conceptual layers:

```
+-----------------------------------------------------------------------+
|                         LAYER 1: PERCEPTION                           |
|  YOLO (Objects & Boxes)  |  PaddleOCR (Text & Price)  | OpenCV (Image) |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                          LAYER 2: EVIDENCE                            |
|             Structured JSON Evidence (Bounding Boxes,                 |
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

For detailed specs, refer to:
- [docs/ARCHITECTURE.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/ARCHITECTURE.md)
- [docs/ROADMAP.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/ROADMAP.md)
- [docs/API_DESIGN.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/API_DESIGN.md)
- [docs/DATA_MODEL.md](file:///c:/Users/raman/OneDrive/Desktop/visiontalkai/docs/DATA_MODEL.md)

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

### 2. Backend Setup & Local Server
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

### 3. Frontend Setup & React Shell
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
Run unit tests (no database required):
```bash
cd backend
pytest -m "not integration"
```

Run integration tests (verifies PostgreSQL readiness):
```bash
cd backend
pytest -m integration
```

Run complete test suite:
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

## 📂 Repository Layout

```
visiontalk-retail-intelligence/
├── backend/
│   ├── app/
│   │   ├── api/v1/health.py     # Liveness & Readiness endpoints
│   │   ├── core/                # Config (CORS, DB, env), exceptions, database session
│   │   ├── schemas/             # Pydantic data schemas
│   │   ├── services/storage/    # StorageService abstraction & LocalStorageProvider
│   │   └── main.py              # FastAPI app entry point
│   ├── tests/                   # Pytest test suite
│   ├── pytest.ini               # Pytest markers config
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # HealthCard component
│   │   ├── services/            # API fetch client
│   │   ├── types/               # TypeScript interface definitions
│   │   ├── App.tsx              # App shell
│   │   └── main.tsx             # React DOM entry
│   ├── tests/                   # Vitest unit tests
│   ├── package.json             # NPM dependencies
│   ├── vite.config.ts           # Vite + Vitest config
│   └── Dockerfile
├── docs/                        # Phase 0 Architecture Specifications
├── docker-compose.yml           # Docker services declaration
├── .env.example                 # Environment template
├── .gitignore
└── README.md
```

---

## 📄 License

This project is licensed under the MIT License.
