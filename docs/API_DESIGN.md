# API Design Specification — VisionTalk Retail Intelligence

## 1. API Standards & Principles

- **Base URL**: `/api/v1`
- **Protocol**: REST over HTTPS
- **Data Format**: JSON (`Content-Type: application/json`)
- **Authentication**: Bearer Token (JWT in `Authorization` header)
- **Error Response Standard**:
  ```json
  {
    "error": {
      "code": "RESOURCE_NOT_FOUND",
      "message": "The requested image ID does not exist.",
      "details": {}
    }
  }
  ```

---

## 2. Core Endpoint Specifications

### 2.1 Authentication & User Management (`/auth`)

#### `POST /api/v1/auth/register`
Creates a new user account and company workspace.

#### `POST /api/v1/auth/login`
Authenticates credentials and returns a JWT access token.
- **Request**: `{ "email": "auditor@retail.com", "password": "..." }`
- **Response**: `{ "access_token": "eyJ...", "token_type": "bearer", "expires_in": 86400 }`

---

### 2.2 Store & Planogram Management (`/stores`)

#### `GET /api/v1/stores`
Lists all stores belonging to the user's company.

#### `POST /api/v1/stores/{store_id}/planograms`
Uploads or updates expected shelf product target configurations (planograms).

---

### 2.3 Image Ingestion & Management (`/images`)

#### `POST /api/v1/images/upload`
Uploads a retail shelf image (`multipart/form-data`).
- **Form Data**: `file` (binary), `store_id` (UUID), `shelf_section` (string).
- **Response**:
  ```json
  {
    "image_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "store_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "file_name": "shelf_auditing_001.jpeg",
    "storage_url": "/storage/images/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d.jpeg",
    "uploaded_at": "2026-08-20T10:15:00Z"
  }
  ```

---

### 2.4 Vision Analysis Engine (`/analysis`)

#### `POST /api/v1/analysis/run`
Triggers full Layer 1 (YOLO + OCR) and Layer 2/3 (Evidence + Retail Analysis) pipeline execution.
- **Request**: `{ "image_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d", "planogram_id": "..." }`
- **Response**: Returns full structured `AnalysisRun` object including detections, OCR, compliance score, and detected issues.

#### `GET /api/v1/analysis/{analysis_id}`
Retrieves existing analysis run results by ID.

---

### 2.5 Grounded Assistant & Chat (`/chat`)

#### `POST /api/v1/chat/query`
Processes user questions against an analysis run using the Question Router.
- **Request**:
  ```json
  {
    "analysis_id": "c1f72818-4228-4c12-8e10-92891bb35111",
    "question": "Why is the compliance score low for this shelf?"
  }
  ```
- **Response**:
  ```json
  {
    "answer": "The compliance score is 65% primarily due to 2 missing expected SKUs (Product C, Product D) and a price tag discrepancy on Product A (displayed: ₹120, expected: ₹110).",
    "grounding_evidence": {
      "missing_skus": ["Product C", "Product D"],
      "price_mismatches": [{"sku": "Product A", "displayed": "₹120", "expected": "₹110"}]
    },
    "router_target": "COMPLIANCE_SERVICE_LLM"
  }
  ```

---

### 2.7 Compliance Rules Engine (`/compliance-rules` & `/compliance`)

#### `POST /api/v1/compliance-rules`
Creates a new retail compliance rule for the tenant company. (Requires ADMIN or MANAGER role).

#### `GET /api/v1/compliance-rules`
Lists active compliance rules filtered by company tenant and optional `store_id`.

#### `GET /api/v1/compliance-rules/{rule_id}`
Retrieves a specific compliance rule by UUID.

#### `PUT /api/v1/compliance-rules/{rule_id}`
Updates a compliance rule (Requires ADMIN or MANAGER role).

#### `DELETE /api/v1/compliance-rules/{rule_id}`
Deletes a compliance rule (Requires ADMIN role).

#### `POST /api/v1/compliance/analyze/{image_id}`
Triggers deterministic compliance rule evaluation against Layer 2 Evidence and Layer 3 Expected-vs-Actual results.
- **Query Parameter**: `force_reanalyze` (boolean, optional default `false`)
- **Response**: Returns structured compliance findings (`PASS`, `FAIL`, `WARNING`), summary counts, and evidence traceability references.

#### `GET /api/v1/compliance/image/{image_id}`
Retrieves compliance findings for an image.

#### `GET /api/v1/compliance/finding/{finding_id}`
Retrieves details for a specific compliance finding.

#### `GET /api/v1/compliance/image/{image_id}/summary`
Retrieves aggregated compliance rule summary metrics (`total_rules`, `passed`, `failed`, `warnings`, `critical_findings`, `high_findings`, `medium_findings`, `low_findings`).

---

### 2.8 Grounded Gemini LLM Explanations (`/llm`)

#### `POST /api/v1/llm/explain/{image_id}`
Generates a grounded natural-language explanation of retail shelf auditing results using the official `google-genai` SDK.
- **Request Body**: `{ "force_reanalyze": false, "question_context": "Focus on missing products..." }`
- **Response**: Returns `LLMExplanationResponse` containing explanation string, bullet-point `key_findings`, `confidence`, `fallback_reason`, and evidence traceability references.

#### `GET /api/v1/llm/explanation/{analysis_run_id}`
Retrieves stored LLM explanation analysis run details by ID.

---

### 2.6 Audit Comparisons (`/comparisons`)

#### `POST /api/v1/comparisons/diff`
Compares two analysis runs (`baseline_analysis_id` vs `current_analysis_id`).
- **Response**: Returns deltas for added products, removed products, movement, and price changes.

---

### 2.7 System & Health Checks (`/health`)

#### `GET /api/v1/health`
Returns component status (API, Database, YOLO model loaded, OCR engine status).
